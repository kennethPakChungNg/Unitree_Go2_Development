#!/usr/bin/env python3
import socket
import time

print("📡 Expansion Dock LiDAR Listener")
print("🎯 Trying to capture data intended for 192.168.123.18")

# Try to bind to the expansion dock's receiving port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # Listen on all interfaces for port 2368
    sock.bind(('0.0.0.0', 2368))
    sock.settimeout(10)
    
    print("⏳ Listening for LiDAR data...")
    
    packet_count = 0
    while packet_count < 10:
        try:
            data, addr = sock.recvfrom(4096)
            packet_count += 1
            print(f"📦 Packet #{packet_count}: {len(data)} bytes from {addr}")
            print(f"🔍 Data preview: {data[:64].hex()}")
            
        except socket.timeout:
            print("⏰ No data in 10 seconds")
            break
            
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sock.close()
    print(f"📊 Total packets captured: {packet_count}")