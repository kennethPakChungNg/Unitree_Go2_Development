import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 2368))
sock.settimeout(5)

print("🚀 UDP Listener running on 0.0.0.0:2368")
print("⏳ Waiting for data...")

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"📬 Received {len(data)} bytes from {addr}")
            print(f"🧾 First 16 bytes: {data[:16].hex()}")
            print(f"💬 ASCII: {data[:16].decode('ascii', errors='replace')}")
        except socket.timeout:
            print("⏰ No data received in last 5 seconds...")
except KeyboardInterrupt:
    print("\n🛑 Listener stopped")