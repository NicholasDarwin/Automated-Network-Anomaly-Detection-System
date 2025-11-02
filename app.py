"""
Flask Web Server - DDoS Attack Target
Serves as the target web application for testing DDoS detection and mitigation.
"""

from flask import Flask, jsonify, request, render_template_string
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
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DDoS Target Server</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 32px;
                text-align: center;
            }
            .status {
                display: inline-block;
                padding: 8px 16px;
                background: #10b981;
                color: white;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 30px;
                margin-top: 10px;
                display: block;
                text-align: center;
                width: fit-content;
                margin-left: auto;
                margin-right: auto;
            }
            .message {
                color: #666;
                text-align: center;
                margin-bottom: 30px;
                font-size: 16px;
            }
            .endpoints-section {
                margin-top: 30px;
            }
            .endpoints-section h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .endpoint-item {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 12px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            .endpoint-item:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            }
            .endpoint-path {
                color: #667eea;
                font-weight: 600;
                font-size: 16px;
                font-family: 'Courier New', monospace;
            }
            .endpoint-desc {
                color: #666;
                margin-top: 5px;
                font-size: 14px;
            }
            .stats-link {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: background 0.3s ease;
                text-align: center;
                width: 100%;
            }
            .stats-link:hover {
                background: #5568d3;
            }
            .endpoint-item a {
                color: inherit;
                text-decoration: none;
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ DDoS Target Server</h1>
            <span class="status">● Online</span>
            <p class="message">Welcome! This server is ready for DDoS testing and mitigation demonstrations.</p>
            
            <div class="endpoints-section">
                <h2>Available Endpoints</h2>
                <div class="endpoint-item">
                    <div class="endpoint-path">GET /</div>
                    <div class="endpoint-desc">Home page - This page</div>
                </div>
                <div class="endpoint-item">
                    <a href="/api/data" target="_blank">
                        <div class="endpoint-path">GET /api/data</div>
                        <div class="endpoint-desc">Data endpoint - Primary target for attacks</div>
                    </a>
                </div>
                <div class="endpoint-item">
                    <a href="/stats">
                        <div class="endpoint-path">GET /api/stats</div>
                        <div class="endpoint-desc">Request statistics - Monitor traffic data</div>
                    </a>
                </div>
                <div class="endpoint-item">
                    <a href="/api/health" target="_blank">
                        <div class="endpoint-path">GET /api/health</div>
                        <div class="endpoint-desc">Health check - Server status</div>
                    </a>
                </div>
            </div>
            
            <a href="/stats" class="stats-link">View Statistics →</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)


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


@app.route('/stats')
def stats_page():
    """Get request statistics page with nice formatting."""
    stats = {
        'total_requests': request_stats['total_requests'],
        'unique_ips': len(request_stats['requests_by_ip']),
        'requests_by_ip': request_stats['requests_by_ip'],
        'recent_requests_count': len(request_stats['requests_timeline'])
    }
    
    # Sort IPs by request count
    sorted_ips = sorted(stats['requests_by_ip'].items(), key=lambda x: x[1], reverse=True)
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="5">
        <title>Server Statistics</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 900px;
                width: 100%;
                margin: 0 auto;
                padding: 40px;
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }
            h1 {
                color: #333;
                font-size: 32px;
            }
            .back-link {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: background 0.3s ease;
            }
            .back-link:hover {
                background: #5568d3;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            .stat-card h3 {
                font-size: 14px;
                font-weight: 400;
                opacity: 0.9;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .stat-card .value {
                font-size: 36px;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .ips-section {
                margin-top: 30px;
            }
            .ips-section h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 24px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .ip-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .ip-table th {
                background: #f8f9fa;
                color: #333;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #667eea;
            }
            .ip-table td {
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
            }
            .ip-table tr:hover {
                background: #f8f9fa;
            }
            .ip-address {
                font-family: 'Courier New', monospace;
                font-weight: 600;
                color: #667eea;
            }
            .request-count {
                font-size: 20px;
                font-weight: 600;
                color: #10b981;
            }
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #999;
                font-size: 18px;
            }
            .refresh-info {
                text-align: center;
                color: #999;
                font-size: 12px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #f0f0f0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Server Statistics</h1>
                <a href="/" class="back-link">← Back to Home</a>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Requests</h3>
                    <div class="value">{{ total_requests }}</div>
                </div>
                <div class="stat-card">
                    <h3>Unique IPs</h3>
                    <div class="value">{{ unique_ips }}</div>
                </div>
                <div class="stat-card">
                    <h3>Recent Requests</h3>
                    <div class="value">{{ recent_requests_count }}</div>
                </div>
            </div>
            
            <div class="ips-section">
                <h2>Requests by IP Address</h2>
                {% if sorted_ips %}
                <table class="ip-table">
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Request Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ip, count in sorted_ips %}
                        <tr>
                            <td class="ip-address">{{ ip }}</td>
                            <td><span class="request-count">{{ count }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    No requests yet. Start making requests to see statistics here!
                </div>
                {% endif %}
            </div>
            
            <div class="refresh-info">
                Page auto-refreshes every 5 seconds
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html_template,
        total_requests=stats['total_requests'],
        unique_ips=stats['unique_ips'],
        recent_requests_count=stats['recent_requests_count'],
        sorted_ips=sorted_ips
    )


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get request statistics for monitoring (JSON API)."""
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

