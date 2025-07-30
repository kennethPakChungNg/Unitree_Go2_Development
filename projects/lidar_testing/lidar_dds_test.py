import sys
sys.path.append('/workspace/development/unitree_sdk2_python')
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize

ChannelFactoryInitialize(0, "eth0")

# Try common LiDAR channel names
channels = ["rt/utlidar", "rt/lidar", "rt/pointcloud", "sensor/lidar"]

for channel in channels:
    try:
        print(f"Testing channel: {channel}")
        # Note: Need proper message type - this is exploratory
    except Exception as e:
        print(f"Channel {channel} failed: {e}")