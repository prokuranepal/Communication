from __future__ import print_function
from dronekit import connect, VehicleMode
import time

from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
DRONE_ID = "0013A200419B5208"

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True)

_location = vehicle.location.global_relative_frame
_attitude = vehicle.attitude
_velocity = vehicle.velocity
_heading = vehicle.heading
_groundspeed = vehicle.groundspeed
_airspeed = vehicle.airspeed

data = {}

data['location'] = {}
data['location']['lat'] = _location.lat
data['location']['lon'] = _location.lon
data['location']['alt'] = _location.alt

data['attitude'] = {}
data['attitude']['roll'] = _attitude.roll
data['attitude']['pitch'] = _attitude.pitch
data['attitude']['yaw'] = _attitude.yaw

data['velocity'] = {}
data['velocity']['vx'] = _velocity[0]
data['velocity']['vy'] = _velocity[1]
data['velocity']['vz'] = _velocity[2]

data['heading'] = _heading
data['groundspeed'] = _groundspeed
data['airspeed'] = _airspeed

data = str(data)



my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()
remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(DRONE_ID))
print("\r\n now sending \r\n")
n = 70 # chunk length
chunks = []

for i in range(0, len(data), n):
    chunks.append(data[i:i+n] )


START_DATA = "$st@"
my_device.send_data(remote_device , START_DATA)

for i in range(len(chunks)):
    DATA_TO_SEND = chunks[i]
    my_device.send_data(remote_device , DATA_TO_SEND)

END_DATA = "$ed@"
my_device.send_data(remote_device,END_DATA)

my_device.close()
print("\r\nsent\r\n")


'''
retrived = ''

for i in range(len(chunks)):
    retrived += chunks[i]

print("retriving")
print(retrived)
print(len(retrived))
'''
