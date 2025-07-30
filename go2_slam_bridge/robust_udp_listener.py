#!/usr/bin/env python3
import socket
import time

def test_udp_reception():
    """Test UDP reception on container"""
    try:
        print(f"📡 Testing UDP reception on container (172.17.0.2)")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Listen on all interfaces within container
        sock.bind(('0.0.0.0', 2368))
        sock.settimeout(20)  # Give more time
        
        print("⏳ Waiting for LiDAR data (20 seconds)...")
        
        packet_count = 0
        start_time = time.time()
        
        while packet_count < 5 and (time.time() - start_time) < 20:
            try:
                data, addr = sock.recvfrom(4096)
                packet_count += 1
                print(f"🎉 SUCCESS! Packet #{packet_count}: {len(data)} bytes from {addr}")
                
            except socket.timeout:
                print(f"⏰ No data received in 20 seconds")
                break
        
        sock.close()
        return packet_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Container UDP Reception Test")
    success = test_udp_reception()
    
    if success:
        print("✅ UDP reception working!")
    else:
        print("❌ No UDP data received")