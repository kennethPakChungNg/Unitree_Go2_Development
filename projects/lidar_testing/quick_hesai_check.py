#!/usr/bin/env python3
"""
Quick Hesai Pandar XT-16 Status Check and Activation
Non-interactive version for Docker testing
"""

import socket
import time
import subprocess
import sys

def check_hesai_power():
    """Check if Hesai XT-16 is powered"""
    print("🔋 Hesai XT-16 Power Check")
    print("=" * 30)
    print("VISUAL INSPECTION NEEDED:")
    print("1. 💡 Look at your Hesai XT-16 sensor")
    print("2. 🔄 Should be spinning (rotating head)")
    print("3. 💙 Blue/Green LED should be on")
    print("4. 🔊 Quiet motor humming sound")
    print()

def ping_hesai_addresses():
    """Test common Hesai IP addresses"""
    print("🔍 Scanning for Hesai XT-16...")
    print("=" * 30)
    
    # Common Hesai IPs
    test_ips = [
        "192.168.1.201",   # Default Hesai
        "192.168.123.201", # Unitree network
        "192.168.0.201",   # Alternative
        "10.5.5.200",      # Another common
    ]
    
    found = []
    for ip in test_ips:
        print(f"🎯 Testing {ip}...")
        try:
            # Use ping command
            result = subprocess.run(['ping', '-n', '1', '-w', '2000', ip], 
                                  capture_output=True, text=True, timeout=5)
            if "TTL=" in result.stdout:
                print(f"  ✅ {ip} responds!")
                found.append(ip)
            else:
                print(f"  ❌ {ip} no response")
        except:
            print(f"  ❌ {ip} ping failed")
    
    return found

def test_udp_data(ip, port=2368):
    """Test for UDP data from Hesai"""
    print(f"📡 Testing UDP data from {ip}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        sock.bind(('', port))
        
        print(f"  👂 Listening for 3 seconds...")
        data, addr = sock.recvfrom(4096)
        
        print(f"  🎉 RECEIVED {len(data)} bytes from {addr[0]}")
        print(f"  📊 First 20 bytes: {data[:20].hex()}")
        
        sock.close()
        return True
        
    except socket.timeout:
        print(f"  ⏰ No data received")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def send_activation_command(ip):
    """Send basic activation command to Hesai"""
    print(f"🚀 Sending activation to {ip}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        
        # Basic Hesai start command
        start_cmd = b'\x47\x74\x00\x01\x00\x00\x00\x00'
        
        sock.sendto(start_cmd, (ip, 9347))
        print(f"  📤 Start command sent")
        
        # Try to get response
        try:
            response, addr = sock.recvfrom(1024)
            print(f"  ✅ Response received: {len(response)} bytes")
        except socket.timeout:
            print(f"  ⏰ No response (normal)")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def main():
    print("🚀 Quick Hesai XT-16 Check")
    print("=" * 40)
    
    # Step 1: Power check (informational)
    check_hesai_power()
    
    # Step 2: Network scan
    found_ips = ping_hesai_addresses()
    
    if not found_ips:
        print("\n❌ No Hesai devices found on network")
        print("\n💡 NEXT STEPS:")
        print("1. Check physical power to Hesai XT-16")
        print("2. Verify network cable connection")
        print("3. May need network configuration:")
        print("   - LiDAR might use different subnet")
        print("   - Default IP: 192.168.1.201")
        print("   - Your network: 192.168.123.x")
        return
    
    # Step 3: Test each found device
    success = False
    for ip in found_ips:
        print(f"\n🎯 Testing device at {ip}")
        
        # First check if already sending data
        if test_udp_data(ip):
            print(f"  ✅ Already active! Data flowing from {ip}")
            success = True
            continue
        
        # Try activation
        if send_activation_command(ip):
            print(f"  ⏰ Waiting 3 seconds after activation...")
            time.sleep(3)
            
            # Test again
            if test_udp_data(ip):
                print(f"  🎉 SUCCESS! Activated {ip}")
                success = True
            else:
                print(f"  ⚠️ Activated but no data yet")
    
    # Results
    print("\n" + "=" * 40)
    if success:
        print("🎉 HESAI XT-16 IS WORKING!")
        print("✅ LiDAR data is flowing")
        print("\n🔄 Next: Create point cloud processor")
    else:
        print("❌ No active Hesai XT-16 found")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check power LED on sensor")
        print("2. Listen for motor spinning")
        print("3. Verify cable connections")
        print("4. Check network configuration")

if __name__ == "__main__":
    main() 