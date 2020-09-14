import time

#Drone import
from drone import Drone

#Import regarding scheduler tasks
from apscheduler.schedulers.background import BackgroundScheduler

#Import for threading
import threading

from socketIO_client_nexus import SocketIO, BaseNamespace

# define background scheduler
sched = BackgroundScheduler()

data = {}
waypoint = {}
DRONE_ID = '#d1'


## Connect to socket
socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
socket_a = socket.define(BaseNamespace,'/JT601')
socket_a.emit("joinPi")

#print("\nConnecting to vehicle on: %s" % connection_string)
print("Connecting to vehicle...")
vehicle = Drone('tcp:127.0.0.1:5762')
print("Connected!!!")

def read_data():
    try:
        #_location = vehicle.location.global_relative_frame
        _location = vehicle.location
    except Exception as e:
        err = {'context':'location','msg':'location not found!!'}
         

    try:
        _attitude = vehicle.attitude
    except Exception as e:
        err = {'context':'attitude','msg':'attitude not found!!'}
         
    
    try:
        _velocity = vehicle.velocity
    except Exception as e:
        err = {'context':'velocity','msg':'velocity not found!!'}
         
    
    try:
        _heading = vehicle.heading
    except Exception as e:
        err = {'context':'heading','msg':'heading not found!!'}
         
        
    try:
        _groundspeed = vehicle.groundspeed
    except Exception as e:
        err = {'context':'groundspeed','msg':'groundspeed not found!!'}
         

    try:    
        _airspeed = vehicle.airspeed
    except Exception as e:
        err = {'context':'airspeed','msg':'airspeed not found!!'}
         
        
    try:
        _mode = vehicle.flight_mode
    except Exception as e:
        err = {'context':'mode','msg':'flight mode not found!!'}
         
        
    try:
        _is_arm = vehicle.is_armed
    except Exception as e:
        err = {'context':'arm','msg':'arm status not found!!'}
         
    
    try:
        _ekf_ok = vehicle.ekf_ok
    except Exception as e:
        err = {'context':'ekf','msg':'ekf status not found!!'}
         
    
    try:
        _status = vehicle.system_status
    except Exception as e:
        err = {'context':'status','msg':'vehicle status not found!!'}
         
        
    try:
        _gps = vehicle.gps_0
    except Exception as e:
        err = {'context':'gps','msg':'gps status not found!!'}
         

    try:    
        _battery = vehicle.battery
    except Exception as e:
        err = {'context':'battery','msg':'battery status not found!!'}
         

    # try:    
    #     _lidar = vehicle.rangefinder.distance
    # except Exception as e:
    #     err = {'context':'lidar','msg':'lidar data not found!!'}
    #      
    
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
    _data = data
    try:
        socket_a.emit('data',_data)
        socket.wait(seconds=1)
    except Exception as e:
        pass

def main():
    #run read_data() every 0.5 seconds
    sched.add_job(read_data, 'interval', seconds=1)
    #run send_data() every 1 seconds
    sched.add_job(send_data,'interval',seconds = 0.5)
    sched.start()

    input()

if __name__ == '__main__':
    main()