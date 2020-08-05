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

#Import regarding logging
import logging

#Import for threading
import threading

#define for logging
#Create and configure logger 
logging.basicConfig(filename="drone.log", 
                    format='%(asctime)s : %(levelname)s :: %(message)s', 
                    filemode='w') 

#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to WARNING. i.e only warning, error, and critical message is shown in log. 
'''
 Thresholds:
 DEBUG
 INFO
 WARNING
 ERROR
 CRITICAL 
'''
logger.setLevel(logging.WARNING) 

# define background scheduler
sched = BackgroundScheduler()

#configure for XBee
PORT = '/dev/ttyUSB0'
BAUD_RATE = 57600
REMOTE_DRONE_ID = "0013A200419B5208"
DRONE_ID = '#d1'
data = {}

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

def read_data():
    try:
        _location_global_relative = vehicle.location.global_relative_frame
        _location_global = vehicle.location.global_frame
    except Exception as e:
        error = {'context':'location','msg':'location not found!!'}
        logger.error(error)

    try:
        _attitude = vehicle.attitude
    except Exception as e:
        error = {'context':'attitude','msg':'attitude not found!!'}
        logger.error(error)
    
    try:
        _velocity = vehicle.velocity
    except Exception as e:
        error = {'context':'velocity','msg':'velocity not found!!'}
        logger.error(error)
    
    try:
        _heading = vehicle.heading
    except Exception as e:
        error = {'context':'heading','msg':'heading not found!!'}
        logger.error(error)
        
    try:
        _groundspeed = vehicle.groundspeed
    except Exception as e:
        error = {'context':'groundspeed','msg':'groundspeed not found!!'}
        logger.error(error)

    try:    
        _airspeed = vehicle.airspeed
    except Exception as e:
        error = {'context':'airspeed','msg':'airspeed not found!!'}
        logger.error(error)
        
    try:
        _mode = vehicle.mode.name
    except Exception as e:
        error = {'context':'mode','msg':'flight mode not found!!'}
        logger.error(error)
        
    try:
        _is_arm = vehicle.armed
    except Exception as e:
        error = {'context':'arm','msg':'arm status not found!!'}
        logger.error(error)
    
    try:
        _ekf_ok = vehicle.ekf_ok
    except Exception as e:
        error = {'context':'ekf','msg':'ekf status not found!!'}
        logger.error(error)
    
    try:
        _status = vehicle.system_status.state
    except Exception as e:
        error = {'context':'status','msg':'vehicle status not found!!'}
        logger.error(error)
        
    try:
        _gps = vehicle.gps_0
    except Exception as e:
        error = {'context':'gps','msg':'gps status not found!!'}
        logger.error(error)

    try:    
        _battery = vehicle.battery
    except Exception as e:
        error = {'context':'battery','msg':'battery status not found!!'}
        logger.error(error)

    try:    
        _lidar = vehicle.rangefinder.distance
    except Exception as e:
        error = {'context':'lidar','msg':'lidar data not found!!'}
        logger.error(error)
    
    data['ID'] = DRONE_ID
    data['lat'] = _location_global_relative.lat
    data['lng'] = _location_global_relative.lon
    data['altr'] = _location_global_relative.alt
    data['alt'] = _location_global.alt
    data['roll'] = _attitude.roll
    data['pitch'] = _attitude.pitch
    data['yaw'] = _attitude.yaw
    data['numSat'] = _gps.satellites_visible
    data['hdop'] = _gps.eph
    data['fix'] = _gps.fix_type
    data['head'] = _heading
    data['gs'] = _groundspeed
    data['as'] = _airspeed
    data['mode'] = _mode
    data['arm'] = _is_arm
    data['ekf'] = _ekf_ok
    data['status'] = _status
    data['lidar'] = _lidar
    data['volt'] = _battery.voltage
    data['conn'] = 'True'
    
    #create a thread instance as t and send data
    #t = threading.Thread(target = send_data, args = (data,))
    #t.start()
    

my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()
remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(REMOTE_DRONE_ID))

def send_data():
    global data
    _data = str(data)
    n = 70 # chunk length
    try:
        START_DATA = "$st@"
        my_device.send_data(remote_device , START_DATA)
        #create a chunk of data and send
        for i in range(0, len(_data), n):
            DATA_TO_SEND = _data[i:i+n]
            my_device.send_data(remote_device , DATA_TO_SEND)
        END_DATA = "$ed@"
        my_device.send_data(remote_device,END_DATA)
    except Exception as e:
            error = {'context':'XBee','msg':'Drone data not sent!!'}
            logging.critical(error)
    



sched.add_job(read_data, 'interval', seconds=0.5)
sched.add_job(send_data,'interval',seconds = 1)
sched.start()


input()
sched.shutdown()
my_device.close()
