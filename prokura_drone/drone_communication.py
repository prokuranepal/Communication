#Import regarding dronekit
from __future__ import print_function
# from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
# import arm_takeoff as arm
import time

#Drone import
from drone import Drone

#Import for missions
# import upload_mission as up
# import mission as mi

#Import regarding XBee
# from digi.xbee.devices import XBeeDevice
# from digi.xbee.devices import RemoteXBeeDevice
# from digi.xbee.models.address import XBee64BitAddress

#Import regarding scheduler tasks
from apscheduler.schedulers.background import BackgroundScheduler
from dronekit import connect, VehicleMode

#Import regarding logging
import logging

#Import for threading
import threading

from socketIO_client_nexus import SocketIO, BaseNamespace


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
BAUD_RATE = 230400
REMOTE_DRONE_ID = "0013A200419B5208"
DRONE_ID = '#d1'
data = {}
waypoint = {}
_send_mission_once = None
sending_label = None


# my_device = XBeeDevice(PORT, BAUD_RATE)
# my_device.open()
# remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(REMOTE_DRONE_ID))

## Connect to socket
socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
socket_a = socket.define(BaseNamespace,'/JT601')
socket_a.emit("joinPi")


#print("\nConnecting to vehicle on: %s" % connection_string)
# print("Connecting to vehicle...")
# vehicle = Drone('127.0.0.1:5760')
# print("Connected!!!")
#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None
data={}

#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=True)
def set_mode_RTL():
    vehicle.set_flight_mode('RTL')

    
def set_mode_LAND():
    vehicle.set_flight_mode('LAND')


def start_mission(var):
    print("flying")
    vehicle.arm_and_takeoff(5,auto_mode=True)

        
def update_mission(location=None):
    print("Location set to :",location)
    try:
        vehicle.mission_upload()#location)
        print (location, "loaded")
    except Exception as e:
        err={'context':'GPS/Mission','msg':'Mission FIle could not be loaded'}
        logger.error(err)


def send_mission():
    global waypoint
    global _send_mission_once
    try:
        waypoint = vehicle.flight_plan
        _send_mission_once = True
        print("Mission send")
    except Exception as e:
        print("eror sending mission", str(e))
        err = {'context':'Mission','msg':'Mission FIle could not be read'}
        logger.error(err)


def read_data():
    try:
        #_location = vehicle.location.global_relative_frame
        _location = vehicle.location
    except Exception as e:
        err = {'context':'location','msg':'location not found!!'}
        logger.error(err)

    try:
        _attitude = vehicle.attitude
    except Exception as e:
        err = {'context':'attitude','msg':'attitude not found!!'}
        logger.error(err)
    
    try:
        _velocity = vehicle.velocity
    except Exception as e:
        err = {'context':'velocity','msg':'velocity not found!!'}
        logger.error(err)
    
    try:
        _heading = vehicle.heading
    except Exception as e:
        err = {'context':'heading','msg':'heading not found!!'}
        logger.error(err)
        
    try:
        _groundspeed = vehicle.groundspeed
    except Exception as e:
        err = {'context':'groundspeed','msg':'groundspeed not found!!'}
        logger.error(err)

    try:    
        _airspeed = vehicle.airspeed
    except Exception as e:
        err = {'context':'airspeed','msg':'airspeed not found!!'}
        logger.error(err)
        
    try:
        _mode = vehicle.flight_mode
    except Exception as e:
        err = {'context':'mode','msg':'flight mode not found!!'}
        logger.error(err)
        
    try:
        _is_arm = vehicle.is_armed
    except Exception as e:
        err = {'context':'arm','msg':'arm status not found!!'}
        logger.error(err)
    
    try:
        _ekf_ok = vehicle.ekf_ok
    except Exception as e:
        err = {'context':'ekf','msg':'ekf status not found!!'}
        logger.error(err)
    
    try:
        _status = vehicle.system_status
    except Exception as e:
        err = {'context':'status','msg':'vehicle status not found!!'}
        logger.error(err)
        
    try:
        _gps = vehicle.gps_0
    except Exception as e:
        err = {'context':'gps','msg':'gps status not found!!'}
        logger.error(err)

    try:    
        _battery = vehicle.battery
    except Exception as e:
        err = {'context':'battery','msg':'battery status not found!!'}
        logger.error(err)

    # try:    
    #     _lidar = vehicle.rangefinder.distance
    # except Exception as e:
    #     err = {'context':'lidar','msg':'lidar data not found!!'}
    #     logger.error(err)
    
    data['ID'] = DRONE_ID
    data['lat'] = _location.lat
    data['lng'] = _location.lon
    data['altr'] = _location.alt
    data['alt'] = _location.altR
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
    #data['lidar'] = _lidar
    data['volt'] = _battery.voltage
    data['conn'] = 'True'
    
    
def send_data():
    global _send_mission_once
    global sending_label
    global data
    global waypoint
    print("working")
    _data_s=""
    _data_d={}
    try:
        if not _send_mission_once:
            sending_label = 'data'
            _data_s = str(data)
            _data_d = data
        else:
            _data_s = str(waypoint)
            _data_d = waypoint
            print("Waypoints:",waypoint)
            sending_label = 'waypoints'
            _send_mission_once = False
    except Exception as e:
        print(str(e))
    n = 70 # chunk length
    try:
        START_DATA = "$st@"
        # my_device.send_data(remote_device , START_DATA)
        #create a chunk of data and send
        for i in range(0, len(_data_s), n):
            DATA_TO_SEND = _data_s[i:i+n]
            # my_device.send_data(remote_device , DATA_TO_SEND)
        END_DATA = "$ed@"
        # my_device.send_data(remote_device,END_DATA)
        print("emitting to",sending_label," ", _data_d)
        socket_a.emit(sending_label,_data_d)
        socket.wait(seconds=1)
    except Exception as e:
        print("emitting to",str(e))
        err = {'context':'XBee','msg':'Drone data not sent!!'}
        logging.critical(err)

    
def hello():
    print("Hello world")

def main():
    #First read mission and send mission
    send_mission()

    #run read_data() every 0.5 seconds
    sched.add_job(read_data, 'interval', seconds=0.1)
    #run send_data() every 1 seconds
    sched.add_job(send_data,'interval',seconds = 0.2)
    sched.start()

    def data_receive_callback(xbee_message):
        message = xbee_message.data.decode()
        if(message == 'LAND'):
            print("Land Mode")
            l = threading.Thread(target = set_mode_LAND)
            l.start()
        elif(message == 'RTL'):
            print("RTL mode")
            r = threading.Thread(target = set_mode_RTL)
            r.start()
        elif(message == 'INIT'):
            print("init mode")
            s = threading.Thread(target = start_mission)
            s.start()
        elif(message[:4] == 'UPDT'):
            location = message[5:]
            u = threading.Thread(target = update_mission,args = (location,))
            u.start()
        elif(message == 'MISS'):
            m = threading.Thread(target = send_mission)
            m.start()

    #add a callback for receive data
    # my_device.add_data_received_callback(data_receive_callback)

    socket_a.on('LAND',set_mode_LAND)
    socket_a.on('RTL',set_mode_RTL)
    socket_a.on('initiate_flight',start_mission)
    socket_a.on('positions',update_mission)
    socket_a.on('mission_download',hello)
    socket.wait(seconds=1)
    input()
    sched.shutdown()
    # my_device.close()

if __name__ == '__main__':
    main()


