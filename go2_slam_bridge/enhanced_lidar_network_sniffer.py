#!/usr/bin/env python3
"""
Enhanced LiDAR Network Sniffer
Tries multiple methods to capture LiDAR data across network boundaries
"""

import socket
import struct
import time
import threading
from scapy.all import sniff, UDP
import subprocess

class EnhancedLidarSniffer:
    def __init__(self):
        self.packet_count = 0
        self.running = True
        
    def method1_direct_udp(self):
        """Method 1: Direct UDP listener"""
        print("🔍 Method 1: Direct UDP listener on port 2368")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', 2368))
            sock.settimeout(5)
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(4096)
                    self.packet_count += 1
                    print(f"📦 Method 1 - Packet #{self.packet_count}: {len(data)} bytes from {addr}")
                    return True
                except socket.timeout:
                    break
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        finally:
            sock.close()
        return False
    
    def method2_promiscuous_sniff(self):
        """Method 2: Network packet sniffing"""
        print("🔍 Method 2: Network packet sniffing for UDP port 2368")
        try:
            def packet_handler(packet):
                if UDP in packet and packet[UDP].dport == 2368:
                    self.packet_count += 1
                    print(f"📦 Method 2 - Packet #{self.packet_count}: {len(packet)} bytes")
                    print(f"🎯 Source: {packet.src} → Destination: {packet.dst}")
                    self.running = False  # Stop after first packet
            
            # Sniff for 10 seconds
            sniff(filter="udp port 2368", prn=packet_handler, timeout=10)
            return self.packet_count > 0
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        return False
    
    def method3_raw_socket(self):
        """Method 3: Raw socket capture"""
        print("🔍 Method 3: Raw socket packet capture")
        try:
            # Create raw socket (requires root)
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.settimeout(10)
            
            while self.running:
                try:
                    packet, addr = sock.recvfrom(65535)
                    # Parse IP header to find UDP packets to port 2368
                    ip_header = struct.unpack('!BBHHHBBH4s4s', packet[:20])
                    protocol = ip_header[6]
                    
                    if protocol == 17:  # UDP
                        udp_header = struct.unpack('!HHHH', packet[20:28])
                        dest_port = udp_header[1]
                        
                        if dest_port == 2368:
                            self.packet_count += 1
                            print(f"📦 Method 3 - Raw packet #{self.packet_count}: {len(packet)} bytes")
                            return True
                            
                except socket.timeout:
                    break
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        finally:
            sock.close()
        return False
    
    def method4_tcpdump_analysis(self):
        """Method 4: Use tcpdump for packet analysis"""
        print("🔍 Method 4: tcpdump network analysis")
        try:
            # Run tcpdump for 10 seconds to capture UDP traffic
            cmd = ["timeout", "10", "tcpdump", "-i", "any", "-c", "10", "udp", "port", "2368", "-n"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                packets_found = [line for line in lines if '2368' in line]
                
                if packets_found:
                    print(f"📦 Method 4 - Found {len(packets_found)} packets!")
                    for i, packet in enumerate(packets_found[:3]):  # Show first 3
                        print(f"   Packet {i+1}: {packet}")
                    return True
                else:
                    print("⏰ Method 4 - No packets found in 10 seconds")
            else:
                print("❌ Method 4 - tcpdump produced no output")
                
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")
        return False

def main():
    print("🚀 Enhanced LiDAR Network Sniffer")
    print("=" * 50)
    print("🎯 Testing multiple capture methods...")
    
    sniffer = EnhancedLidarSniffer()
    
    # Try methods in order of likelihood to work
    methods = [
        ("Direct UDP Listener", sniffer.method1_direct_udp),
        ("tcpdump Analysis", sniffer.method4_tcpdump_analysis),
        ("Raw Socket Capture", sniffer.method3_raw_socket),
        ("Promiscuous Sniffing", sniffer.method2_promiscuous_sniff),
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying {method_name}...")
        try:
            success = method_func()
            if success:
                print(f"✅ {method_name} SUCCESS!")
                print(f"📊 Total packets found: {sniffer.packet_count}")
                break
            else:
                print(f"⚠️ {method_name} - No data detected")
        except KeyboardInterrupt:
            print(f"\n🛑 {method_name} stopped by user")
            break
        except Exception as e:
            print(f"❌ {method_name} error: {e}")
    
    else:
        print("\n❌ All methods failed to detect LiDAR data")
        print("\n💡 Recommendations:")
        print("   1. Verify LiDAR destination IP in web interface")
        print("   2. Check if LiDAR is actually transmitting")
        print("   3. Try Solution A (Windows computer as destination)")
    
    print(f"\n📊 Final packet count: {sniffer.packet_count}")

if __name__ == "__main__":
    main()