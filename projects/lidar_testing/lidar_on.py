import sys
sys.path.append('/workspace/development/unitree_sdk2_python')
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.idl.std_msgs.msg.dds_ import String_
from unitree_sdk2py.idl.default import std_msgs_msg_dds__String_

ChannelFactoryInitialize(0, "eth0")
publisher = ChannelPublisher("rt/utlidar/switch", String_)
publisher.Init()

cmd = std_msgs_msg_dds__String_()
cmd.data = "ON"
publisher.Write(cmd)
print("✅ LiDAR ON")