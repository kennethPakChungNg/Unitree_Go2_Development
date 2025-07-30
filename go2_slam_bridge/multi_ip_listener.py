#!/usr/bin/env python3
import socket
import threading
import time

def listen_on_ip(ip, port=2368):
    """Listen for UDP packets on specific IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        sock.settimeout(10)
        print(f"📡 Listening on {ip}:{port}")
        
        packet_count = 0
        while packet_count < 5:  # Just get a few packets to test
            try:
                data, addr = sock.recvfrom(4096)
                packet_count += 1
                print(f"🎉 SUCCESS on {ip}! Packet #{packet_count}: {len(data)} bytes from {addr}")
            except socket.timeout:
                print(f"⏰ No data on {ip} in 10 seconds")
                break
        
        sock.close()
        return packet_count
        
    except Exception as e:
        print(f"❌ Error on {ip}: {e}")
        return 0

# Test both Docker IPs simultaneously
print("🔍 Testing UDP reception on both Docker IPs...")

# Try both IPs
thread1 = threading.Thread(target=listen_on_ip, args=('192.168.65.3',))
thread2 = threading.Thread(target=listen_on_ip, args=('192.168.65.6',))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("🏁 Test complete!")