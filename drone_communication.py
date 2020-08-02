from __future__ import print_function
from dronekit import connect, VehicleMode
import time

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

print(data)