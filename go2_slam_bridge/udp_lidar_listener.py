#!/usr/bin/env python3
import socket
import time

print("📡 UDP LiDAR Listener Starting...")
print("⏳ Listening for broadcasts on port 2368...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 2368))  # Listen on all interfaces
sock.settimeout(10)  # 10 second timeout

packet_count = 0
try:
    while packet_count < 5:  # Only try 5 packets
        try:
            data, addr = sock.recvfrom(2048)
            packet_count += 1
            print(f"📦 Packet #{packet_count}: {len(data)} bytes from {addr}")
            print(f"🔍 First 32 bytes: {data[:32].hex()}")
            
        except socket.timeout:
            print("⏰ No data received in 10 seconds")
            break
            
except KeyboardInterrupt:
    print("🛑 Stopped by user")
finally:
    sock.close()
    print(f"📊 Total packets: {packet_count}")