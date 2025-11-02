"""
Mitigation System
Throttles and blocks suspicious IPs detected by the anomaly detector.
"""

import time
import threading
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MitigationSystem:
    """Mitigates DDoS attacks by throttling and blocking suspicious IPs."""
    
    def __init__(self, server_url='http://127.0.0.1:5000', throttle_rate=10, block_duration=300):
        """
        Initialize the mitigation system.
        
        Args:
            server_url: URL of the target server
            throttle_rate: Requests per minute allowed for throttled IPs
            block_duration: Duration in seconds to block IPs
        """
        self.server_url = server_url
        self.throttle_rate = throttle_rate  # requests per minute
        self.block_duration = block_duration  # seconds
        
        # Track throttled and blocked IPs
        self.throttled_ips = {}  # {ip: {'rate': X, 'window_start': timestamp, 'requests': count}}
        self.blocked_ips = {}  # {ip: 'blocked_until': timestamp}
        
        # Request tracking per IP
        self.ip_requests = defaultdict(list)  # {ip: [timestamps]}
        
        self.running = False
        self.mitigation_thread = None
        
    def throttle_ip(self, ip, rate_limit=None):
        """
        Throttle an IP address.
        
        Args:
            ip: IP address to throttle
            rate_limit: Requests per minute allowed (defaults to throttle_rate)
        """
        if rate_limit is None:
            rate_limit = self.throttle_rate
            
        self.throttled_ips[ip] = {
            'rate': rate_limit,
            'window_start': datetime.now(),
            'requests': 0
        }
        logger.info(f"Throttled IP {ip} at {rate_limit} requests/minute")
        
    def block_ip(self, ip, duration=None):
        """
        Block an IP address for a specified duration.
        
        Args:
            ip: IP address to block
            duration: Block duration in seconds (defaults to block_duration)
        """
        if duration is None:
            duration = self.block_duration
            
        blocked_until = datetime.now() + timedelta(seconds=duration)
        self.blocked_ips[ip] = {'blocked_until': blocked_until}
        logger.warning(f"Blocked IP {ip} until {blocked_until}")
        
        # Also remove from throttled list if present
        if ip in self.throttled_ips:
            del self.throttled_ips[ip]
            
    def unblock_ip(self, ip):
        """Remove IP from blocked list."""
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            logger.info(f"Unblocked IP {ip}")
            
    def is_blocked(self, ip):
        """
        Check if an IP is currently blocked.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is blocked, False otherwise
        """
        if ip not in self.blocked_ips:
            return False
            
        blocked_info = self.blocked_ips[ip]
        if datetime.now() < blocked_info['blocked_until']:
            return True
        else:
            # Block expired, remove it
            self.unblock_ip(ip)
            return False
            
    def is_throttled(self, ip):
        """
        Check if an IP is currently throttled.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is throttled, False otherwise
        """
        return ip in self.throttled_ips
        
    def should_allow_request(self, ip):
        """
        Determine if a request from an IP should be allowed.
        
        Args:
            ip: IP address making the request
            
        Returns:
            True if request should be allowed, False otherwise
        """
        # Check if IP is blocked
        if self.is_blocked(ip):
            return False
            
        # Check if IP is throttled
        if ip in self.throttled_ips:
            throttle_info = self.throttled_ips[ip]
            now = datetime.now()
            
            # Reset window if it's been more than a minute
            if (now - throttle_info['window_start']).total_seconds() > 60:
                throttle_info['window_start'] = now
                throttle_info['requests'] = 0
                
            # Check rate limit
            if throttle_info['requests'] >= throttle_info['rate']:
                logger.debug(f"Rate limit exceeded for IP {ip}")
                return False
            else:
                throttle_info['requests'] += 1
                return True
                
        return True
        
    def apply_mitigation(self, suspicious_ips):
        """
        Apply mitigation measures to suspicious IPs.
        
        Args:
            suspicious_ips: List of suspicious IP addresses
        """
        for ip_info in suspicious_ips:
            ip = ip_info if isinstance(ip_info, str) else ip_info.get('ip', ip_info)
            
            # Skip if already blocked
            if self.is_blocked(ip):
                continue
                
            # Get anomaly score if available
            anomaly_score = ip_info.get('anomaly_score', -1) if isinstance(ip_info, dict) else -1
            
            # Block highly suspicious IPs (very negative scores)
            if anomaly_score < -0.5:
                self.block_ip(ip, duration=self.block_duration)
            else:
                # Throttle moderately suspicious IPs
                self.throttle_ip(ip, rate_limit=self.throttle_rate)
                
    def cleanup_expired_blocks(self):
        """Remove expired IP blocks."""
        now = datetime.now()
        expired_ips = [
            ip for ip, info in self.blocked_ips.items()
            if now >= info['blocked_until']
        ]
        
        for ip in expired_ips:
            self.unblock_ip(ip)
            
    def mitigation_loop(self, interval=10):
        """
        Main mitigation loop to clean up expired blocks.
        
        Args:
            interval: Loop interval in seconds
        """
        logger.info("Mitigation system started")
        
        while self.running:
            try:
                self.cleanup_expired_blocks()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in mitigation loop: {e}")
                time.sleep(interval)
                
        logger.info("Mitigation system stopped")
        
    def start_mitigation(self, interval=10):
        """
        Start the mitigation system.
        
        Args:
            interval: Cleanup interval in seconds
        """
        if not self.running:
            self.running = True
            self.mitigation_thread = threading.Thread(target=self.mitigation_loop, args=(interval,))
            self.mitigation_thread.daemon = True
            self.mitigation_thread.start()
            logger.info("Started mitigation system")
            
    def stop_mitigation(self):
        """Stop the mitigation system."""
        if self.running:
            self.running = False
            if self.mitigation_thread:
                self.mitigation_thread.join(timeout=5)
            logger.info("Stopped mitigation system")
            
    def get_status(self):
        """Get current mitigation status."""
        return {
            'blocked_ips': {
                ip: info['blocked_until'].isoformat()
                for ip, info in self.blocked_ips.items()
            },
            'throttled_ips': {
                ip: f"{info['requests']}/{info['rate']} req/min"
                for ip, info in self.throttled_ips.items()
            },
            'total_blocked': len(self.blocked_ips),
            'total_throttled': len(self.throttled_ips)
        }


if __name__ == '__main__':
    mitigation = MitigationSystem()
    mitigation.start_mitigation()
    
    try:
        while True:
            time.sleep(10)
            status = mitigation.get_status()
            logger.info(f"Mitigation status: {status}")
    except KeyboardInterrupt:
        logger.info("Stopping mitigation system...")
        mitigation.stop_mitigation()

