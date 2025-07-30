#!/usr/bin/env python3
import socket
import time

print("🔍 Simple LiDAR Test Starting...")
print("💾 Memory usage should be minimal")

try:
    # Basic socket test
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.connect(('192.168.123.20', 2368))
    print("✅ LiDAR socket: Connected")
    
    # Try to receive data
    sock.settimeout(5)
    data = sock.recv(1024)
    print(f"📦 Received: {len(data)} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sock.close()
    print("🏁 Test complete")

time.sleep(2)  # Keep running briefly