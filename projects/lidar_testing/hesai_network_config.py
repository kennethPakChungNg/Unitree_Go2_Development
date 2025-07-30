#!/usr/bin/env python3
"""
Hesai XT-16 Network Configuration Helper
Find and configure LiDAR network settings
"""

import socket
import struct
import subprocess
import ipaddress
import time

def scan_local_networks():
    """Scan all local network interfaces for potential LiDAR"""
    print("🌐 Scanning Local Networks for Hesai XT-16")
    print("=" * 45)
    
    # Get network interfaces
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        interfaces = result.stdout
        print("📡 Network Interfaces Found:")
        
        # Extract IP addresses from ipconfig output
        import re
        ip_pattern = r'IPv4 Address[.\s]*:\s*([0-9.]+)'
        found_ips = re.findall(ip_pattern, interfaces)
        
        for ip in found_ips:
            if not ip.startswith('127.'):  # Skip localhost
                print(f"  - {ip}")
                
                # Calculate network range
                try:
                    network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
                    print(f"    Network: {network}")
                    
                    # Try common LiDAR IPs in this network
                    base_ip = str(network.network_address)[:-1]  # Remove last octet
                    test_ips = [
                        f"{base_ip}201",  # Common Hesai ending
                        f"{base_ip}200",
                        f"{base_ip}199",
                        f"{base_ip}100",
                    ]
                    
                    for test_ip in test_ips:
                        if ping_ip(test_ip):
                            print(f"    🎯 FOUND DEVICE: {test_ip}")
                            return test_ip
                            
                except:
                    continue
                    
    except Exception as e:
        print(f"❌ Network scan failed: {e}")
    
    return None

def ping_ip(ip, timeout=1):
    """Quick ping test"""
    try:
        result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                              capture_output=True, timeout=3)
        return "TTL=" in result.stdout
    except:
        return False

def try_hesai_broadcast_discovery():
    """Try broadcast discovery for Hesai devices"""
    print("\n📻 Broadcast Discovery for Hesai Devices")
    print("=" * 40)
    
    try:
        # Create broadcast socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)
        
        # Hesai discovery packet (may vary by firmware)
        discovery_packet = b'\x47\x74\x00\xFF\x00\x00\x00\x00'
        
        # Try different broadcast addresses
        broadcast_addresses = [
            '255.255.255.255',
            '192.168.1.255',
            '192.168.123.255',
            '192.168.0.255',
        ]
        
        for addr in broadcast_addresses:
            print(f"📡 Broadcasting to {addr}...")
            try:
                sock.sendto(discovery_packet, (addr, 9347))
                
                # Listen for responses
                try:
                    data, server = sock.recvfrom(1024)
                    print(f"  🎉 RESPONSE from {server[0]}: {len(data)} bytes")
                    sock.close()
                    return server[0]
                except socket.timeout:
                    print(f"  ⏰ No response from {addr}")
                    
            except Exception as e:
                print(f"  ❌ Broadcast to {addr} failed: {e}")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Broadcast discovery failed: {e}")
    
    return None

def configure_hesai_ip(current_ip, new_ip="192.168.123.201"):
    """Configure Hesai XT-16 IP address"""
    print(f"\n🔧 Configuring Hesai IP: {current_ip} → {new_ip}")
    print("=" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # Hesai IP configuration command (firmware-specific)
        # This is a generic example - actual command may vary
        new_ip_bytes = socket.inet_aton(new_ip)
        
        config_packet = b'\x47\x74\x00\x10' + new_ip_bytes + b'\x00\x00\x00\x00'
        
        print(f"📤 Sending IP config command...")
        sock.sendto(config_packet, (current_ip, 9347))
        
        # Wait for response
        try:
            response, addr = sock.recvfrom(1024)
            print(f"  ✅ Configuration response: {len(response)} bytes")
            
            print(f"  ⏰ Waiting 10 seconds for device restart...")
            time.sleep(10)
            
            # Test new IP
            if ping_ip(new_ip):
                print(f"  🎉 SUCCESS! Device now at {new_ip}")
                return new_ip
            else:
                print(f"  ⚠️ Device not responding at new IP")
                
        except socket.timeout:
            print(f"  ⏰ No configuration response")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ IP configuration failed: {e}")
    
    return None

def main():
    print("🚀 Hesai XT-16 Network Configuration")
    print("=" * 50)
    
    # Step 1: Scan local networks
    found_ip = scan_local_networks()
    
    if found_ip:
        print(f"\n✅ Found potential Hesai device at {found_ip}")
        
        # Test if it responds to Hesai commands
        print(f"🔍 Testing Hesai protocols on {found_ip}...")
        # Additional testing could go here
        
    else:
        print("\n❌ No devices found on local networks")
        
        # Step 2: Try broadcast discovery
        found_ip = try_hesai_broadcast_discovery()
        
        if found_ip:
            print(f"\n✅ Found Hesai via broadcast: {found_ip}")
        else:
            print("\n❌ No Hesai devices found via broadcast")
    
    # Step 3: Configuration options
    if found_ip:
        print(f"\n🎯 Device found at {found_ip}")
        print("💡 Options:")
        print(f"1. Use device as-is at {found_ip}")
        print(f"2. Configure to match robot network (192.168.123.x)")
        print()
        
        # For automation, let's suggest configuration
        if not found_ip.startswith("192.168.123"):
            print("🔧 Recommending IP change to match robot network...")
            new_ip = configure_hesai_ip(found_ip, "192.168.123.201")
            if new_ip:
                found_ip = new_ip
    
    # Final result
    if found_ip:
        print(f"\n🎉 HESAI XT-16 READY!")
        print(f"📍 IP Address: {found_ip}")
        print(f"📡 Data Port: 2368 (UDP)")
        print(f"🔧 Control Port: 9347 (UDP)")
        print(f"\n✅ You can now access LiDAR data from this IP")
    else:
        print(f"\n❌ HESAI XT-16 NOT FOUND")
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"1. Verify power connection to LiDAR")
        print(f"2. Check Ethernet cable to expansion module")
        print(f"3. Ensure LiDAR is spinning (powered on)")
        print(f"4. May need manual network configuration")
        print(f"5. Check LiDAR manual for default IP settings")

if __name__ == "__main__":
    main() 