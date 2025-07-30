import sys
sys.path.append('/workspace/development/unitree_sdk2_python')
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient

# Import proper message types for Go2-W
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_

def LowStateHandler(msg: LowState_):
    """Handle incoming low-level state data which may include sensor information"""
    print("📡 Received robot state data:")
    print(f"  - IMU: {msg.imu_state}")
    print(f"  - Battery: {msg.power_v}V, {msg.power_a}A")
    print(f"  - Foot sensors: {msg.foot_force}")
    if hasattr(msg, 'foot_force_est'):
        print(f"  - Foot force estimates: {msg.foot_force_est}")
    
    # Check for any LiDAR-related data in the state
    print(f"  - Message attributes: {[attr for attr in dir(msg) if not attr.startswith('_')]}")

print("🚀 Testing Go2-W Robot State and Sensor Access")
print("="*50)

# Method 1: Try Robot State Client (RPC-based)
print("\n1️⃣ Testing Robot State Client (RPC)")
ChannelFactoryInitialize(0, "eth0")
client = RobotStateClient()
client.Init()

# Check what services are available
try:
    code, services = client.ServiceList()
    if code == 0 and services:
        print("✅ Available services:")
        for service in services:
            print(f"  - {service.name}: status={service.status}, protected={service.protect}")
    else:
        print(f"⚠️ ServiceList returned code: {code}")
except Exception as e:
    print(f"❌ ServiceList failed: {e}")

# Method 2: Try Direct DDS Subscription (more likely to work)
print("\n2️⃣ Testing Direct DDS Subscription")
try:
    # Subscribe to low-level state which should contain sensor data
    state_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
    state_subscriber.Init(LowStateHandler, 10)
    
    print("✅ Subscribed to rt/lowstate topic")
    print("⏰ Waiting for data (10 seconds)...")
    
    import time
    time.sleep(10)
    
except Exception as e:
    print(f"❌ DDS subscription failed: {e}")

# Method 3: Check for LiDAR-specific topics
print("\n3️⃣ Checking for LiDAR-specific topics")
try:
    # Import LiDAR state message if available
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import LidarState_
    
    def LidarStateHandler(msg: LidarState_):
        print("🎯 LiDAR State Received:")
        print(f"  - Firmware: {msg.firmware_version}")
        print(f"  - Rotation speed: {msg.sys_rotation_speed}")
        print(f"  - Cloud frequency: {msg.cloud_frequency}")
        print(f"  - Packet loss: {msg.cloud_packet_loss_rate}%")
        print(f"  - Point cloud size: {msg.cloud_size}")
    
    lidar_subscriber = ChannelSubscriber("rt/utlidar/state", LidarState_)
    lidar_subscriber.Init(LidarStateHandler, 10)
    
    print("✅ Subscribed to LiDAR state topic")
    print("⏰ Waiting for LiDAR data (10 seconds)...")
    
    time.sleep(10)
    
except ImportError:
    print("⚠️ LidarState message type not found - trying alternative topics")
    
    # Try generic point cloud subscription
    try:
        # Check if we can access point cloud data directly
        print("🔍 Checking for point cloud topics...")
        # This would require proper point cloud message types
        print("�� Try: rostopic list | grep lidar (if ROS bridge is active)")
        print("💡 Try: Check /utlidar/cloud topic with appropriate message type")
    except Exception as e:
        print(f"❌ Point cloud check failed: {e}")

print("\n" + "="*50)
print("🏁 Robot State and Sensor Test Complete")