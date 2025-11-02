"""
Flask Web Server - DDoS Attack Target
Serves as the target web application for testing DDoS detection and mitigation.
"""

from flask import Flask, jsonify, request
import time
import logging
from datetime import datetime
from flask_middleware import init_mitigation_middleware, require_mitigation_check

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store request statistics
request_stats = {
    'total_requests': 0,
    'requests_by_ip': {},
    'requests_timeline': []
}


@app.route('/')
def index():
    """Home page endpoint."""
    return jsonify({
        'message': 'Welcome to the DDoS Target Server',
        'status': 'online',
        'endpoints': {
            '/': 'Home page',
            '/api/data': 'Data endpoint',
            '/api/stats': 'Request statistics',
            '/api/health': 'Health check'
        }
    })


@app.route('/api/data', methods=['GET'])
@require_mitigation_check
def get_data():
    """API data endpoint - primary target for attacks."""
    client_ip = request.remote_addr
    timestamp = datetime.now()
    
    # Update statistics
    request_stats['total_requests'] += 1
    if client_ip not in request_stats['requests_by_ip']:
        request_stats['requests_by_ip'][client_ip] = 0
    request_stats['requests_by_ip'][client_ip] += 1
    request_stats['requests_timeline'].append({
        'ip': client_ip,
        'timestamp': timestamp.isoformat(),
        'endpoint': '/api/data'
    })
    
    logger.info(f"Request from {client_ip} to /api/data")
    
    # Simulate some processing time
    time.sleep(0.01)
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': request_stats['total_requests'],
            'message': 'Sample API data',
            'timestamp': timestamp.isoformat(),
            'client_ip': client_ip
        }
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get request statistics for monitoring."""
    return jsonify({
        'total_requests': request_stats['total_requests'],
        'unique_ips': len(request_stats['requests_by_ip']),
        'requests_by_ip': request_stats['requests_by_ip'],
        'recent_requests_count': len(request_stats['requests_timeline'])
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'operational'
    })


def init_app(mitigation_system=None):
    """
    Initialize Flask app with optional mitigation system.
    
    Args:
        mitigation_system: Optional MitigationSystem instance
    """
    if mitigation_system:
        init_mitigation_middleware(app, mitigation_system)
        logger.info("Mitigation system integrated with Flask app")
    return app


if __name__ == '__main__':
    logger.info("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

