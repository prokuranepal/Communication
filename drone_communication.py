#Import regarding dronekit
from __future__ import print_function
from dronekit import connect, VehicleMode
import time

#Import regarding XBee
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress

#Import regarding scheduler tasks
from apscheduler.schedulers.background import BackgroundScheduler

# define background scheduler
sched = BackgroundScheduler()

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

def read_and_send_data():
    _location = vehicle.location.global_relative_frame
    _attitude = vehicle.attitude
    _velocity = vehicle.velocity
    _heading = vehicle.heading
    _groundspeed = vehicle.groundspeed
    _airspeed = vehicle.airspeed
    _mode = vehicle.mode.name
    _is_arm = vehicle.armed
    _ekf_ok = vehicle.ekf_ok
    _status = vehicle.system_status.state
    _gps = vehicle.gps_0
    _battery = vehicle.battery
    _lidar = vehicle.rangefinder.distance

    print("Alt:",_location.alt)
    print("Sat:",_gps.satellites_visible)
    print("Hdop:",_gps.eph)
    print("fix:",_gps.fix_type)
    print("Head:",_heading)
    print("GS:",_groundspeed)
    print("AS",_airspeed)
    print("mode:",_mode)
    print("Arm:",_is_arm)
    print("EKF:",_ekf_ok)
    print("Status:",_status)
    print("lidar:",_lidar)
    print("Volt:",_battery.voltage)
    print("\r\n ")


sched.add_job(read_and_send_data, 'interval', seconds=1)
sched.start()
input()
sched.shutdown()




'''
data = {}

data['location'] = {}
data['location']['lat'] = _location.lat
data['location']['lon'] = _location.lon
data['location']['altR'] = _location.alt

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


count = 0
while True:
    START_DATA = "$st@"
    my_device.send_data(remote_device , START_DATA)

    for i in range(len(chunks)):
        DATA_TO_SEND = chunks[i]
        my_device.send_data(remote_device , DATA_TO_SEND)

    END_DATA = "$ed@"
    my_device.send_data(remote_device,END_DATA)

    count += 1
    if (count == 100):
        my_device.close()
        break
    print("\r\nsent:",count)
    time.sleep(0.1)

'''