import sys
sys.path.append('/workspace/development/unitree_sdk2_python')

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.idl.default import std_msgs_msg_dds__String_

# Initialize once
ChannelFactoryInitialize(0, "eth0")

publisher = ChannelPublisher("rt/utlidar/switch", String_)
publisher.Init()

def switch_lidar(status):
    cmd = std_msgs_msg_dds__String_()
    cmd.data = status
    publisher.Write(cmd)
    print(f"✅ LiDAR: {status}")

if __name__ == '__main__':
    print("🔄 Turning LiDAR ON...")
    switch_lidar("ON")
    
    input("Press Enter to turn OFF...")
    switch_lidar("OFF")