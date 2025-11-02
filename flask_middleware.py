"""
Flask Middleware for DDoS Mitigation
Integrates the mitigation system with Flask to block/throttle requests in real-time.
"""

from flask import request, jsonify
from functools import wraps
from mitigation_system import MitigationSystem
import logging

logger = logging.getLogger(__name__)

# Global mitigation system instance (will be set by app)
mitigation_system = None


def set_mitigation_system(system):
    """Set the global mitigation system instance."""
    global mitigation_system
    mitigation_system = system


def mitigation_check():
    """Middleware function to check if request should be allowed."""
    if mitigation_system is None:
        return None  # No mitigation system set, allow all requests
        
    client_ip = request.remote_addr
    
    # Check if IP is blocked
    if mitigation_system.is_blocked(client_ip):
        logger.warning(f"Blocked request from {client_ip}")
        return jsonify({
            'error': 'IP blocked',
            'message': 'Your IP address has been temporarily blocked due to suspicious activity.'
        }), 403
        
    # Check if IP should be throttled
    if not mitigation_system.should_allow_request(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests from this IP. Please slow down.'
        }), 429
        
    return None  # Allow request


def require_mitigation_check(f):
    """Decorator to add mitigation check to a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check mitigation before processing request
        response = mitigation_check()
        if response:
            return response
        return f(*args, **kwargs)
    return decorated_function


def init_mitigation_middleware(app, mitigation_sys):
    """
    Initialize mitigation middleware for Flask app.
    
    Args:
        app: Flask application instance
        mitigation_sys: MitigationSystem instance
    """
    global mitigation_system
    mitigation_system = mitigation_sys
    
    # Register before_request handler
    @app.before_request
    def check_mitigation():
        """Check mitigation before each request."""
        response = mitigation_check()
        if response:
            return response
            
    logger.info("Mitigation middleware initialized for Flask app")

