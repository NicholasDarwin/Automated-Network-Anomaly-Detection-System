"""
Anomaly Detection System
Detects DDoS attacks using machine learning and statistical analysis.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalous traffic patterns indicative of DDoS attacks."""
    
    def __init__(self, contamination=0.1):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies (0.1 = 10%)
        """
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, traffic_data):
        """
        Extract features from traffic data for anomaly detection.
        
        Args:
            traffic_data: List of traffic entries with timestamps and request info
            
        Returns:
            DataFrame with extracted features
        """
        if not traffic_data:
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(traffic_data)
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['second'] = df['timestamp'].dt.second
        
        # Group by time windows (e.g., 1-minute intervals)
        df['time_window'] = df['timestamp'].dt.floor('1Min')
        
        # Calculate request rates per IP
        ip_rates = defaultdict(list)
        for entry in traffic_data:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                requests_by_ip = entry.get('requests_by_ip', {})
                
                for ip, count in requests_by_ip.items():
                    ip_rates[ip].append({
                        'timestamp': entry_time,
                        'requests': count
                    })
            except:
                continue
                
        # Calculate features for each IP
        features = []
        for ip, requests in ip_rates.items():
            if len(requests) > 1:
                req_df = pd.DataFrame(requests)
                req_df = req_df.sort_values('timestamp')
                
                # Calculate request rate (requests per minute)
                time_diff = (req_df['timestamp'].max() - req_df['timestamp'].min()).total_seconds() / 60
                if time_diff > 0:
                    request_rate = len(req_df) / time_diff
                else:
                    request_rate = len(req_df)
                    
                # Calculate request variance
                request_variance = req_df['requests'].var() if len(req_df) > 1 else 0
                
                # Calculate maximum requests in any single time period
                max_requests = req_df['requests'].max()
                
                features.append({
                    'ip': ip,
                    'request_rate': request_rate,
                    'request_variance': request_variance,
                    'max_requests': max_requests,
                    'total_requests': req_df['requests'].sum()
                })
                
        if features:
            features_df = pd.DataFrame(features)
            return features_df
        else:
            return pd.DataFrame()
            
    def detect_anomalies(self, traffic_data):
        """
        Detect anomalies in traffic data.
        
        Args:
            traffic_data: List of traffic entries
            
        Returns:
            Dictionary with anomaly detection results
        """
        if not traffic_data:
            return {'anomalies': [], 'suspicious_ips': []}
            
        # Extract features
        features_df = self.extract_features(traffic_data)
        
        if features_df.empty:
            return {'anomalies': [], 'suspicious_ips': []}
            
        # Prepare features for ML model
        feature_columns = ['request_rate', 'request_variance', 'max_requests', 'total_requests']
        X = features_df[feature_columns].fillna(0).values
        
        # Scale features
        if not self.is_trained:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
        else:
            X_scaled = self.scaler.transform(X)
            
        # Predict anomalies (1 = normal, -1 = anomaly)
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # Identify suspicious IPs
        suspicious_ips = []
        for idx, (ip, pred, score) in enumerate(zip(features_df['ip'], predictions, anomaly_scores)):
            if pred == -1:  # Anomaly detected
                suspicious_ips.append({
                    'ip': ip,
                    'anomaly_score': float(score),
                    'request_rate': float(features_df.iloc[idx]['request_rate']),
                    'max_requests': int(features_df.iloc[idx]['max_requests']),
                    'total_requests': int(features_df.iloc[idx]['total_requests'])
                })
                
        # Statistical threshold detection (additional layer)
        threshold_suspicious = self.statistical_threshold_detection(features_df)
        
        # Combine results
        all_suspicious = set()
        for ip_info in suspicious_ips:
            all_suspicious.add(ip_info['ip'])
        for ip_info in threshold_suspicious:
            all_suspicious.add(ip_info['ip'])
            
        return {
            'anomalies': suspicious_ips + threshold_suspicious,
            'suspicious_ips': list(all_suspicious),
            'total_ips_analyzed': len(features_df),
            'anomalies_detected': len(all_suspicious)
        }
        
    def statistical_threshold_detection(self, features_df, rate_threshold=10, max_requests_threshold=50):
        """
        Detect suspicious IPs using statistical thresholds.
        
        Args:
            features_df: DataFrame with IP features
            rate_threshold: Requests per minute threshold
            max_requests_threshold: Maximum requests threshold
            
        Returns:
            List of suspicious IP information
        """
        suspicious = []
        
        for _, row in features_df.iterrows():
            if (row['request_rate'] > rate_threshold or 
                row['max_requests'] > max_requests_threshold):
                suspicious.append({
                    'ip': row['ip'],
                    'anomaly_score': -1.0,  # High suspicion
                    'request_rate': float(row['request_rate']),
                    'max_requests': int(row['max_requests']),
                    'total_requests': int(row['total_requests']),
                    'reason': 'statistical_threshold'
                })
                
        return suspicious
        
    def analyze_recent_traffic(self, traffic_monitor, time_window_minutes=5):
        """
        Analyze recent traffic for anomalies.
        
        Args:
            traffic_monitor: TrafficMonitor instance
            time_window_minutes: Time window to analyze
            
        Returns:
            Dictionary with detection results
        """
        recent_activity = traffic_monitor.get_recent_activity(minutes=time_window_minutes)
        
        if not recent_activity:
            logger.warning("No recent activity to analyze")
            return {'anomalies': [], 'suspicious_ips': []}
            
        logger.info(f"Analyzing {len(recent_activity)} recent traffic entries")
        
        results = self.detect_anomalies(recent_activity)
        
        if results['suspicious_ips']:
            logger.warning(f"Detected {len(results['suspicious_ips'])} suspicious IPs: {results['suspicious_ips']}")
        else:
            logger.info("No anomalies detected in recent traffic")
            
        return results


if __name__ == '__main__':
    # Example usage
    from traffic_monitor import TrafficMonitor
    
    monitor = TrafficMonitor()
    monitor.start_monitoring(interval=5)
    
    detector = AnomalyDetector()
    
    try:
        while True:
            import time
            time.sleep(30)  # Run detection every 30 seconds
            
            results = detector.analyze_recent_traffic(monitor, time_window_minutes=5)
            
            if results['suspicious_ips']:
                print(f"\n🚨 ALERT: Detected {len(results['suspicious_ips'])} suspicious IPs:")
                for ip in results['suspicious_ips']:
                    print(f"  - {ip}")
                    
    except KeyboardInterrupt:
        logger.info("Stopping detector...")
        monitor.stop_monitoring()

