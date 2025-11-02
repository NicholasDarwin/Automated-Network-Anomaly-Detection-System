# DDoS Attack Simulation and Mitigation System

A Python-based tool that simulates DDoS attacks on a local web server, detects them via traffic anomalies, and mitigates by throttling suspicious IPs.

## Project Overview

This project demonstrates a complete DDoS detection and mitigation system:

1. **Flask Web Server** - Serves as the target web application
2. **DDoS Simulator** - Simulates various DDoS attacks using Scapy
3. **Traffic Monitor** - Collects and logs network traffic
4. **Anomaly Detector** - Uses machine learning to identify suspicious patterns
5. **Mitigation System** - Throttles and blocks suspicious IPs

## Features

- **Attack Simulation**: Supports SYN flood, HTTP flood, and Slowloris attacks
- **Traffic Monitoring**: Real-time collection and logging of network traffic
- **Anomaly Detection**: Uses Isolation Forest (scikit-learn) to detect anomalies
- **IP Mitigation**: Automatic throttling and blocking of suspicious IPs
- **Docker Support**: Easy deployment in Docker containers

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- Linux/macOS/WSL for Windows (Scapy requires root/admin privileges)

## Installation

### Local Installation

1. Clone or navigate to the project directory:
```bash
cd "Cyber Project"
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. For Scapy to work properly, you may need root/admin privileges on Linux/macOS:
```bash
sudo pip install -r requirements.txt  # Linux/macOS
```

### Docker Installation

1. Build and start containers:
```bash
docker-compose up --build
```

This will start:
- Web server on port 5000
- Protection system monitoring and protecting the server

## Usage

### 1. Start the Flask Web Server

In one terminal:
```bash
python app.py
```

The server will start on `http://localhost:5000`

### 2. Start the Protection System

In another terminal:
```bash
python main.py
```

The protection system will:
- Monitor traffic from the Flask server
- Detect anomalies every 30 seconds
- Automatically throttle or block suspicious IPs

### 3. Run a DDoS Attack Simulation

In a third terminal (Linux/macOS, requires root):
```bash
sudo python ddos_simulator.py --attack http --duration 60 --rate 100
```

Or without root (HTTP flood only):
```bash
python ddos_simulator.py --attack http --duration 60 --rate 100
```

Attack options:
- `--attack syn` - SYN flood attack (requires root)
- `--attack http` - HTTP flood attack
- `--attack slowloris` - Slowloris attack
- `--duration 60` - Attack duration in seconds
- `--rate 100` - Request/packet rate per second

### 4. Monitor the Results

The protection system will:
1. Detect the attack via anomaly detection
2. Identify suspicious IPs
3. Apply mitigation (throttling or blocking)
4. Log all activities

Check the logs in the terminal or view `traffic_log.json` for detailed statistics.

## API Endpoints

The Flask server provides the following endpoints:

- `GET /` - Home page with API information
- `GET /api/data` - Primary target endpoint for attacks
- `GET /api/stats` - Request statistics
- `GET /api/health` - Health check endpoint

## Configuration

### Protection System Parameters

You can configure the protection system when starting `main.py`:

```bash
python main.py \
  --server http://127.0.0.1:5000 \
  --monitor-interval 5 \
  --detection-interval 30 \
  --throttle-rate 10 \
  --block-duration 300
```

Parameters:
- `--server` - Target server URL
- `--monitor-interval` - Traffic monitoring interval (seconds)
- `--detection-interval` - Anomaly detection interval (seconds)
- `--throttle-rate` - Requests per minute for throttled IPs
- `--block-duration` - Block duration for blocked IPs (seconds)

## Project Structure

```
.
├── app.py                  # Flask web server
├── ddos_simulator.py       # DDoS attack simulator
├── traffic_monitor.py      # Traffic monitoring system
├── anomaly_detector.py     # Anomaly detection using ML
├── mitigation_system.py    # IP throttling/blocking system
├── main.py                # Main orchestration script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # This file
```

## How It Works

1. **Traffic Monitoring**: The `TrafficMonitor` continuously collects statistics from the Flask server's `/api/stats` endpoint.

2. **Anomaly Detection**: The `AnomalyDetector` analyzes recent traffic patterns using:
   - Isolation Forest (machine learning)
   - Statistical threshold detection
   - Request rate analysis per IP

3. **Mitigation**: The `MitigationSystem` automatically applies mitigation:
   - **Throttling**: Limits suspicious IPs to N requests per minute
   - **Blocking**: Temporarily blocks highly suspicious IPs

4. **Attack Simulation**: The `DDoSSimulator` can generate various attack types for testing.

## Security Notes

⚠️ **WARNING**: This tool is for **EDUCATIONAL and RESEARCH purposes only**. 

- Do not use this tool against any systems you do not own or have explicit permission to test
- DDoS attacks are illegal in most jurisdictions
- Only use on isolated local networks or dedicated test environments
- Ensure compliance with local laws and regulations

## Troubleshooting

### Scapy Permission Errors
- On Linux/macOS: Use `sudo` when running the DDoS simulator
- On Windows: Run PowerShell as Administrator
- Alternative: Use HTTP flood attacks which don't require root privileges

### Port Already in Use
- Change the Flask server port in `app.py` if port 5000 is occupied
- Update the `--server` URL in `main.py` accordingly

### Docker Issues
- Ensure Docker and Docker Compose are installed and running
- Check logs: `docker-compose logs`
- Rebuild containers: `docker-compose up --build --force-recreate`

## Future Enhancements

- Web dashboard for real-time monitoring
- More sophisticated ML models (LSTM, autoencoders)
- Integration with firewall rules
- Distributed detection across multiple servers
- GraphQL API endpoints
- Rate limiting middleware for Flask

## License

This project is for educational purposes only.

## Contributing

This is an educational project. Contributions and improvements are welcome!

## Author

Created as part of a cybersecurity project demonstration.

