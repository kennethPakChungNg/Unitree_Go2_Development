import sys, time
sys.path.append('/workspace/development/unitree_sdk2_python')
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_

ChannelFactoryInitialize(0, "eth0")

channels = ["rt/utlidar", "rt/lidar", "pointcloud", "sensor_msgs/PointCloud2"]
for ch in channels:
    try:
        print(f"Testing {ch}...")
        sub = ChannelSubscriber(ch, PointCloud2_)
        sub.Init()
        data = sub.Read()  # Remove SetTimeout
        print(f"✅ {ch}: {data is not None}")
    except Exception as e:
        print(f"❌ {ch}: {e}")