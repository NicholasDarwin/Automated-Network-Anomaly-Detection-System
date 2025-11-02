"""
Demo Script - Run DDoS Detection and Mitigation System
Demonstrates the complete system in action.
"""

import time
import subprocess
import threading
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_server():
    """Run the Flask web server."""
    logger.info("Starting Flask web server...")
    subprocess.run([sys.executable, "app.py"])


def run_protection_system():
    """Run the DDoS protection system."""
    logger.info("Starting DDoS protection system...")
    time.sleep(2)  # Wait for server to start
    subprocess.run([sys.executable, "main.py"])


def run_attack_simulation():
    """Run a DDoS attack simulation."""
    logger.info("Waiting before starting attack simulation...")
    time.sleep(10)  # Wait for system to initialize
    logger.info("Starting DDoS attack simulation...")
    subprocess.run([
        sys.executable, 
        "ddos_simulator.py",
        "--attack", "http",
        "--duration", "60",
        "--rate", "50"
    ])


def main():
    """Main demo function."""
    print("=" * 60)
    print("DDoS Detection and Mitigation System - Demo")
    print("=" * 60)
    print("\nThis demo will:")
    print("1. Start the Flask web server")
    print("2. Start the protection system")
    print("3. Simulate a DDoS attack")
    print("\nPress Ctrl+C to stop all components")
    print("=" * 60)
    
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Start protection system in a thread
    protection_thread = threading.Thread(target=run_protection_system, daemon=True)
    protection_thread.start()
    
    # Wait a bit, then start attack
    time.sleep(15)
    
    # Start attack simulation in a thread
    attack_thread = threading.Thread(target=run_attack_simulation, daemon=True)
    attack_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nStopping demo...")
        logger.info("All components should stop automatically")
        sys.exit(0)


if __name__ == '__main__':
    main()

