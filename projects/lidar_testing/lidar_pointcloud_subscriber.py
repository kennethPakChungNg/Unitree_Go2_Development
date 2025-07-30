import sys
import time
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LidarState_

ChannelFactoryInitialize(0, "eth0")

channels = [
    ("rt/utlidar/cloud", PointCloud2_),
    ("rt/lidar/pointcloud", PointCloud2_), 
    ("rt/utlidar/state", LidarState_),
    ("rt/pointcloud", PointCloud2_)
]

for channel_name, msg_type in channels:
    print(f"Testing {channel_name}...")
    try:
        subscriber = ChannelSubscriber(channel_name, msg_type)
        subscriber.Init()
        
        # Quick test without timeout
        data = subscriber.Read()
        if data:
            print(f"✅ Got data from {channel_name}!")
            print(f"   Data type: {type(data)}")
            break
        else:
            print(f"   No data")
    except Exception as e:
        print(f"   Error: {e}")