"""
Main DDoS Detection and Mitigation System
Orchestrates the traffic monitoring, anomaly detection, and mitigation systems.
"""

import time
import signal
import sys
import logging
import threading
from traffic_monitor import TrafficMonitor
from anomaly_detector import AnomalyDetector
from mitigation_system import MitigationSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DDOSProtectionSystem:
    """Main DDoS protection system orchestrating all components."""
    
    def __init__(self, server_url='http://127.0.0.1:5000', 
                 monitor_interval=5, detection_interval=30,
                 throttle_rate=10, block_duration=300):
        """
        Initialize the DDoS protection system.
        
        Args:
            server_url: URL of the target server
            monitor_interval: Traffic monitoring interval (seconds)
            detection_interval: Anomaly detection interval (seconds)
            throttle_rate: Requests per minute for throttled IPs
            block_duration: Block duration for blocked IPs (seconds)
        """
        self.server_url = server_url
        self.monitor_interval = monitor_interval
        self.detection_interval = detection_interval
        self.running = False
        
        # Initialize components
        self.traffic_monitor = TrafficMonitor(server_url=server_url)
        self.anomaly_detector = AnomalyDetector()
        self.mitigation_system = MitigationSystem(
            server_url=server_url,
            throttle_rate=throttle_rate,
            block_duration=block_duration
        )
        
        # Detection thread
        self.detection_thread = None
        
    def detection_loop(self):
        """Main detection loop."""
        logger.info("Detection loop started")
        
        while self.running:
            try:
                # Analyze recent traffic
                results = self.anomaly_detector.analyze_recent_traffic(
                    self.traffic_monitor,
                    time_window_minutes=5
                )
                
                # Apply mitigation if suspicious IPs detected
                if results['suspicious_ips']:
                    logger.warning(f"Detected {len(results['suspicious_ips'])} suspicious IPs")
                    
                    # Apply mitigation
                    suspicious_ip_info = results.get('anomalies', [])
                    if suspicious_ip_info:
                        self.mitigation_system.apply_mitigation(suspicious_ip_info)
                    else:
                        # Create basic IP info if not provided
                        ip_info = [{'ip': ip, 'anomaly_score': -1} for ip in results['suspicious_ips']]
                        self.mitigation_system.apply_mitigation(ip_info)
                        
                    # Log status
                    status = self.mitigation_system.get_status()
                    logger.info(f"Mitigation status: {status['total_blocked']} blocked, "
                              f"{status['total_throttled']} throttled")
                    
                time.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(self.detection_interval)
                
        logger.info("Detection loop stopped")
        
    def start(self):
        """Start the DDoS protection system."""
        logger.info("Starting DDoS protection system...")
        
        self.running = True
        
        # Start traffic monitoring
        self.traffic_monitor.start_monitoring(interval=self.monitor_interval)
        
        # Start mitigation system
        self.mitigation_system.start_mitigation()
        
        # Start detection loop
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        logger.info("DDoS protection system started")
        logger.info(f"Monitoring server: {self.server_url}")
        logger.info(f"Detection interval: {self.detection_interval}s")
        logger.info(f"Throttle rate: {self.mitigation_system.throttle_rate} req/min")
        logger.info(f"Block duration: {self.mitigation_system.block_duration}s")
        
    def stop(self):
        """Stop the DDoS protection system."""
        logger.info("Stopping DDoS protection system...")
        
        self.running = False
        
        # Stop components
        self.traffic_monitor.stop_monitoring()
        self.mitigation_system.stop_mitigation()
        
        # Wait for detection thread
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
            
        logger.info("DDoS protection system stopped")
        
    def get_status(self):
        """Get system status."""
        monitor_stats = self.traffic_monitor.get_statistics()
        mitigation_status = self.mitigation_system.get_status()
        
        return {
            'monitor': monitor_stats,
            'mitigation': mitigation_status,
            'running': self.running
        }


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Shutdown signal received")
    if 'system' in globals():
        system.stop()
    sys.exit(0)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='DDoS Detection and Mitigation System')
    parser.add_argument('--server', default='http://127.0.0.1:5000', 
                       help='Target server URL')
    parser.add_argument('--monitor-interval', type=int, default=5,
                       help='Traffic monitoring interval (seconds)')
    parser.add_argument('--detection-interval', type=int, default=30,
                       help='Anomaly detection interval (seconds)')
    parser.add_argument('--throttle-rate', type=int, default=10,
                       help='Requests per minute for throttled IPs')
    parser.add_argument('--block-duration', type=int, default=300,
                       help='Block duration for blocked IPs (seconds)')
    
    args = parser.parse_args()
    
    # Create system
    global system
    system = DDOSProtectionSystem(
        server_url=args.server,
        monitor_interval=args.monitor_interval,
        detection_interval=args.detection_interval,
        throttle_rate=args.throttle_rate,
        block_duration=args.block_duration
    )
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start system
    system.start()
    
    try:
        # Run until interrupted
        while True:
            time.sleep(10)
            # Periodically log status
            status = system.get_status()
            logger.info(f"System status: {status['mitigation']['total_blocked']} blocked, "
                       f"{status['mitigation']['total_throttled']} throttled")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        system.stop()


if __name__ == '__main__':
    main()

