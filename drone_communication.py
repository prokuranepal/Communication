#Import regarding dronekit
from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
import arm_takeoff as arm
import time

#Import for missions
import upload_mission as up
import mission as mi

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
waypoint = {}
_send_mission_once = None

my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()
remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(REMOTE_DRONE_ID))


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
print("Connected!!!")

def set_mode_RTL():
    global vehicle
    fix_type=0
    try:
        fix_type=vehicle.gps_0.fix_type
    except Exception as e:
        pass
    if fix_type >1:
        vehicle.mode = VehicleMode("RTL")
        print ("Vehicle mode set to RTL")
        warn = {'context':'INFO','msg':'Vehicle mode set to RTL'}
        logger.warning(warn)
    
def set_mode_LAND():
    global vehicle
    fix_type=0
    try:
        fix_type=vehicle.gps_0.fix_type
    except Exception as e:
        pass
    if fix_type >1:
        vehicle.mode=VehicleMode("LAND")
        print("Vehicle mode set to LAND")
        warn = {'context':'INFO','msg':'Vehicle mode set to LAND'}
        logger.warning(warn)

def start_mission():
    try:
        height =vehicle.location.global_relative_frame.alt
        if vehicle.is_armable and height <= 4: # and not flight_checker: #checking if vehicle is armable and fly command is genuine

            print("FLIGHT INITIATED BY USER")
            # Copter should arm in GUIDED mode
            vehicle.mode    = VehicleMode("GUIDED")
            vehicle.armed   = True
            # Confirm vehicle armed before attempting to take off
            while not vehicle.armed:
                print (" Waiting for arming...")
                time.sleep(1)
            arm.arm_and_takeoff(vehicle,4) #arm and takeoff upto 4 meters
            vehicle.mode = VehicleMode("AUTO") #switch vehicle mode to auto
           
            #UNCOMMENT FOR PLANE TAKEOFF
            # vehicle.mode    = VehicleMode("GUIDED")
            # vehicle.armed   = True
            # # Confirm vehicle armed before attempting to take off
            # while not vehicle.armed:
            #     print (" Waiting for arming...")
            #     time.sleep(1)
            # vehicle.mode = VehicleMode("AUTO") #switch vehicle mode to auto'''
            # flight_checker=True
        else:
            fix_type=0
            try:
                fix_type=vehicle.gps_0.fix_type
            except Exception as e:
                pass
            if fix_type > 1:
                vehicle.mode=VehicleMode("AUTO")
                print ("Vehicle mode set to AUTO")

    except Exception as e:
        err = {'context':'Prearm','msg':'Pre-arm check failed!!!'}
        logger.error(err)

        
def update_mission(location):
    print("Location set to :",type(location))
    try:
        up.upload_mission(vehicle,location)
        print (location, "loaded")
    except Exception as e:
        err={'context':'GPS/Mission','msg':'Mission FIle could not be loaded'}
        logger.error(err)


def send_mission():
    #read mission
    global waypoint
    global send_mission_once
    try:
        print("\nReading mission")
        waypoint=mi.save_mission(vehicle)
        send_mission_once = True
        print("\nMission read")
        #if waypoint is read, then set send_mission_once to True so that, mission can be sent instead of data.
    except Exception as e:
        err = {'context':'Mission','msg':'Mission FIle could not be read'}
        logger.error(err)
    



def read_data():
    try:
        _location_global_relative = vehicle.location.global_relative_frame
        _location_global = vehicle.location.global_frame
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
        _mode = vehicle.mode.name
    except Exception as e:
        err = {'context':'mode','msg':'flight mode not found!!'}
        logger.error(err)
        
    try:
        _is_arm = vehicle.armed
    except Exception as e:
        err = {'context':'arm','msg':'arm status not found!!'}
        logger.error(err)
    
    try:
        _ekf_ok = vehicle.ekf_ok
    except Exception as e:
        err = {'context':'ekf','msg':'ekf status not found!!'}
        logger.error(err)
    
    try:
        _status = vehicle.system_status.state
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

    try:    
        _lidar = vehicle.rangefinder.distance
    except Exception as e:
        err = {'context':'lidar','msg':'lidar data not found!!'}
        logger.error(err)
    
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
    
    
    
def send_data():
    global send_mission_once

    if not send_mission_once:
        global data
        _data = str(data)
    else:
        global waypoint
        _data = str(waypoint)
        send_mission_once = False
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
            err = {'context':'XBee','msg':'Drone data not sent!!'}
            logging.critical(err)
    


def main():
    #First read mission and send mission
    send_mission()

    #run read_data() every 0.5 seconds
    sched.add_job(read_data, 'interval', seconds=0.5)
    #run send_data() every 1 seconds
    sched.add_job(send_data,'interval',seconds = 1)
    sched.start()

    def data_receive_callback(xbee_message):
        message = xbee_message.data.decode()
        if(message == 'LAND'):
            l = threading.Thread(target = set_mode_LAND)
            l.start()
        elif(message == 'RTL'):
            r = threading.Thread(target = set_mode_RTL)
            r.start()
        elif(message == 'INIT'):
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
    my_device.add_data_received_callback(data_receive_callback)

    input()
    sched.shutdown()
    my_device.close()

if __name__ == '__main__':
    main()


