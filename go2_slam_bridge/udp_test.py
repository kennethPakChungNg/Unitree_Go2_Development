import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 2368))
sock.settimeout(10)

print("🚀 UDP Listener running on 0.0.0.0:2368")
print("⏳ Waiting for data...")

try:
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"📬 Received {len(data)} bytes from {addr}")
            print(f"🧾 Data: {data[:16].hex(' ')}...")
            # Send response back
            sock.sendto(b"ACK", addr)
            print(f"📤 Sent ACK to {addr}")
        except socket.timeout:
            print("⏰ No data received...")
            continue
except KeyboardInterrupt:
    print("\n🛑 Listener stopped")
finally:
    sock.close()