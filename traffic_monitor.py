"""
Traffic Monitoring System
Monitors and logs network traffic for anomaly detection.
"""

import time
import threading
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrafficMonitor:
    """Monitors network traffic and collects statistics."""
    
    def __init__(self, server_url='http://127.0.0.1:5000', log_file='traffic_log.json'):
        """
        Initialize the traffic monitor.
        
        Args:
            server_url: URL of the target server
            log_file: File to store traffic logs
        """
        self.server_url = server_url
        self.log_file = log_file
        self.running = False
        self.monitor_thread = None
        
        # Statistics storage
        self.stats = {
            'requests_by_ip': defaultdict(int),
            'requests_by_time': defaultdict(int),
            'requests_by_endpoint': defaultdict(int),
            'response_times': [],
            'failed_requests': 0,
            'timeline': []
        }
        
        # Load existing logs if available
        self.load_logs()
        
    def load_logs(self):
        """Load existing traffic logs from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.stats.update(data)
                logger.info(f"Loaded traffic logs from {self.log_file}")
            except Exception as e:
                logger.warning(f"Could not load logs: {e}")
                
    def save_logs(self):
        """Save traffic logs to file."""
        try:
            # Convert defaultdicts to regular dicts for JSON serialization
            stats_to_save = {
                'requests_by_ip': dict(self.stats['requests_by_ip']),
                'requests_by_time': dict(self.stats['requests_by_time']),
                'requests_by_endpoint': dict(self.stats['requests_by_endpoint']),
                'response_times': self.stats['response_times'][-1000:],  # Keep last 1000
                'failed_requests': self.stats['failed_requests'],
                'timeline': self.stats['timeline'][-1000:]  # Keep last 1000
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(stats_to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving logs: {e}")
            
    def collect_stats_from_server(self):
        """Collect statistics from the Flask server's /api/stats endpoint."""
        try:
            response = requests.get(f"{self.server_url}/api/stats", timeout=2)
            if response.status_code == 200:
                server_stats = response.json()
                return server_stats
        except Exception as e:
            logger.debug(f"Could not fetch server stats: {e}")
        return None
        
    def monitor_loop(self, interval=5):
        """
        Main monitoring loop.
        
        Args:
            interval: Monitoring interval in seconds
        """
        logger.info("Traffic monitor started")
        
        while self.running:
            try:
                # Collect stats from server
                server_stats = self.collect_stats_from_server()
                
                if server_stats:
                    # Update statistics
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.stats['requests_by_time'][current_time] = server_stats.get('total_requests', 0)
                    
                    # Update IP-based statistics
                    for ip, count in server_stats.get('requests_by_ip', {}).items():
                        self.stats['requests_by_ip'][ip] = count
                    
                    # Record in timeline
                    self.stats['timeline'].append({
                        'timestamp': datetime.now().isoformat(),
                        'total_requests': server_stats.get('total_requests', 0),
                        'unique_ips': server_stats.get('unique_ips', 0),
                        'requests_by_ip': server_stats.get('requests_by_ip', {})
                    })
                    
                # Periodically save logs
                if len(self.stats['timeline']) % 10 == 0:
                    self.save_logs()
                    
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(interval)
                
        logger.info("Traffic monitor stopped")
        
    def start_monitoring(self, interval=5):
        """
        Start the monitoring thread.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, args=(interval,))
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info(f"Started monitoring with {interval}s interval")
            
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            self.save_logs()
            logger.info("Stopped monitoring")
            
    def get_statistics(self):
        """Get current statistics."""
        return {
            'requests_by_ip': dict(self.stats['requests_by_ip']),
            'requests_by_time': dict(self.stats['requests_by_time']),
            'requests_by_endpoint': dict(self.stats['requests_by_endpoint']),
            'total_failed': self.stats['failed_requests'],
            'timeline_count': len(self.stats['timeline'])
        }
        
    def get_recent_activity(self, minutes=5):
        """
        Get recent activity within specified time window.
        
        Args:
            minutes: Time window in minutes
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = []
        
        for entry in self.stats['timeline']:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time >= cutoff_time:
                    recent.append(entry)
            except:
                continue
                
        return recent


if __name__ == '__main__':
    monitor = TrafficMonitor()
    monitor.start_monitoring(interval=5)
    
    try:
        while True:
            time.sleep(10)
            stats = monitor.get_statistics()
            logger.info(f"Monitor stats: {stats}")
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        monitor.stop_monitoring()

