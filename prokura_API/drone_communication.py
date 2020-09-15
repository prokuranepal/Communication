#Import regarding dronekit
from __future__ import print_function
# from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
# import arm_takeoff as arm
import time

#Drone import
from prokura_drone.drone import Drone
from command_queue import CommandQueue

#Import for missions
# import upload_mission as up
# import mission as mi

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
command_queue = CommandQueue()

my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()
remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(REMOTE_DRONE_ID))

## Connect to socket
#socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
socket = SocketIO('http://582eb8945f7c.ngrok.io', verify =True)
socket_a = socket.define(BaseNamespace,'/JT601')
socket_a.emit("joinDrone")


#print("\nConnecting to vehicle on: %s" % connection_string)
print("Connecting to vehicle...")
vehicle = Drone('tcp:127.0.0.1:5762')
print("Connected!!!")


def on_reconnect():
    socket_a.emit("joinDrone")

def is_timestamp_received(time):
    if command_queue.__contains__(time):
        return True
    else:
        return False

def timestamp_add(time):
    command_queue._put(time)


def set_mode_RTL(var = None):
    time = var['timestamp']
    if not is_timestamp_received(time):
        timestamp_add(time)
        vehicle.set_flight_mode('RTL')
        print("RTL mode set")
    else:
        print("RTL Message came again so ignoring")

def set_mode_LAND(var = None):
    print("Came here")
    time = var['timestamp']
    if not is_timestamp_received(time):
        timestamp_add(time)
        vehicle.set_flight_mode('LAND')
        print("LAND mode set")
    else:
        print("LAND Message came again so ignoring")


def start_mission(var = None):
    time = var['timestamp']
    if not is_timestamp_received(time):
        timestamp_add(time)
        vehicle.arm_and_takeoff(5,auto_mode=True)
        print("Arm and takeoff")
    else:
        print("Arm & takeoff came again so ignoring")

        
def update_mission(location=None):
    print("Location set to :",location)
    try:
        vehicle.mission_upload()#location)
        print (location, "loaded")
    except Exception as e:
        err={'context':'GPS/Mission','msg':'Mission FIle could not be loaded'}
        logger.error(err)

def new_mission_update_send(var):
    time = var['timestamp']
    mission_waypoints = var['mission']['waypoints']
    vehicle.new_mission_upload(mission_waypoints)


def send_mission(var = None):
    #time = var['timestamp']
    if not is_timestamp_received(var):
        timestamp_add(var)
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
    else:
        print("Send mission came again so ignoring")


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
    data['timestamp'] = time.time()
    
def send_data():
    global _send_mission_once
    global sending_label
    if not _send_mission_once:
        global data
        sending_label = 'data'
        _data_s = str(data)
        _data_d = data
    else:
        global waypoint
        _data_s = str(waypoint)
        _data_d = waypoint
        print("Waypoints:",waypoint)
        sending_label = 'waypoints'
        _send_mission_once = False
    n = 70 # chunk length
    try:
        START_DATA = "$st@"
        my_device.send_data(remote_device , START_DATA)
        #create a chunk of data and send
        for i in range(0, len(_data_s), n):
            DATA_TO_SEND = _data_s[i:i+n]
            my_device.send_data(remote_device , DATA_TO_SEND)
        END_DATA = "$ed@"
        my_device.send_data(remote_device,END_DATA)
    except Exception as e:
            err = {'context':'XBee','msg':'Drone data not sent from xbee!!'}
            logging.critical(err)

    try:
        socket_a.emit(sending_label,_data_d)
        socket.wait(seconds=1)
    except Exception as e:
        pass
    
def hello(var):
    print("Timestamp for hello:",var)

def send_home_position(var):
    home = {
        'lat':vehicle._home.lat,
        'lng':vehicle._home.lon
    }
    socket_a.emit('homePosition',home)
    print("Home sent")

def flush_rx_data():
    if(command_queue._size > 2): # Always maintain atleast 2 command in the set so that recent message wont be deleted
        a = command_queue._get()
        print("Popped out ",a," From queue")
        pass

def main():
    #First read mission and send mission
    home = {
        'lat':vehicle._home.lat,
        'lng':vehicle._home.lon
    }
    socket_a.emit('homePosition',home)
    print("Home sent")
    send_mission()

    #run read_data() every 0.5 seconds
    sched.add_job(read_data, 'interval', seconds=0.5)
    #run send_data() every 1 seconds
    sched.add_job(send_data,'interval',seconds = 1)
    sched.add_job(flush_rx_data,'interval',seconds = 3)
    sched.start()

    def data_receive_callback(xbee_message):
        message = xbee_message.data.decode()
        if(message[:4] == 'LAND'):
            print("Land Mode")
            timestamp = message[5:]
            l = threading.Thread(target = set_mode_LAND,args = (timestamp,))
            l.start()
        elif(message[:3] == 'RTL'):
            print("RTL mode")
            timestamp = message[4:]
            r = threading.Thread(target = set_mode_RTL,args = (timestamp,))
            r.start()
        elif(message[:4] == 'INIT'):
            print("init mode")
            timestamp = message[5:]
            s = threading.Thread(target = start_mission,args = (timestamp,))
            s.start()
        elif(message[:4] == 'UPDT'):
            location = message[5:]
            u = threading.Thread(target = update_mission,args = (location,))
            u.start()
        elif(message[:4] == 'MISS'):
            timestamp = message[5:]
            m = threading.Thread(target = send_mission,args = (timestamp,))
            m.start()

    #add a callback for receive data
    my_device.add_data_received_callback(data_receive_callback)

    socket_a.on('LAND',set_mode_LAND)
    socket_a.on('RTL',set_mode_RTL)
    socket_a.on('initiateFlight',start_mission)
    socket_a.on('positions',update_mission)
    socket_a.on('getMission',send_mission)
    socket_a.on('mission',new_mission_update_send)
    socket_a.on('homePosition',send_home_position)
    socket_a.on('reconnect',on_reconnect)

    input()
    sched.shutdown()
    my_device.close()

if __name__ == '__main__':
    main()


