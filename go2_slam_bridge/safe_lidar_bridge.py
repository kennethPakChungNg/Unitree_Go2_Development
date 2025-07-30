#!/usr/bin/env python3
import socket
import time
import signal
import sys

class SafeLidarBridge:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        print('\n🛑 Stopping safely...')
        self.running = False
        sys.exit(0)
        
    def test_lidar(self):
        print("🔍 Safe LiDAR Bridge Test")
        
        # Try for only 30 seconds max
        start_time = time.time()
        timeout = 30
        
        while self.running and (time.time() - start_time) < timeout:
            try:
                print("📡 Attempting connection...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.bind(('0.0.0.0', 2368))
                
                print("⏳ Waiting for data (5 seconds)...")
                data, addr = sock.recvfrom(2048)
                print(f"🎉 SUCCESS! Received {len(data)} bytes from {addr}")
                return True
                
            except socket.timeout:
                print("⏰ No data - LiDAR not transmitting")
            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                sock.close()
                
            time.sleep(2)  # Wait before retry
            
        print(f"🏁 Test complete after {time.time() - start_time:.1f} seconds")
        return False

if __name__ == "__main__":
    bridge = SafeLidarBridge()
    bridge.test_lidar()