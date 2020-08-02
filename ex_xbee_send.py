from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress


PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
DRONE_ID = "0013A200419B5208"
DATA_TO_SEND = "Hello World"

my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()

remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(DRONE_ID))
my_device.send_data(remote_device , DATA_TO_SEND)
my_device.close()