# Dockerfile for DDoS Detection and Mitigation System

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tcpdump \
    iproute2 \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY traffic_monitor.py .
COPY anomaly_detector.py .
COPY mitigation_system.py .
COPY ddos_simulator.py .
COPY main.py .

# Expose Flask port
EXPOSE 5000

# Default command: run Flask server
CMD ["python", "app.py"]

