from digi.xbee.devices import XBeeDevice
PORT = '/dev/ttyUSB0'
BAUD_RATE = 57600

device = XBeeDevice(PORT, BAUD_RATE)
device.open()

# Get the 64-bit address of the device.
addr_64 = device.get_64bit_addr()
# Get the node identifier of the device.
node_id = device.get_node_id()
# Get the hardware version of the device.
hardware_version = device.get_hardware_version()
# Get the firmware version of the device.
firmware_version = device.get_firmware_version()

print("MAC ADDRESS = ",addr_64)
print("Node ID = ",node_id)