import socket
import serial, time
import threading
import queue
from socketIO_client_nexus import SocketIO, BaseNamespace
UDP_IP = "127.0.0.1"
UDP_PORT = 14550
MESSAGE = b"mavlink message"



print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

class HandleServer():
    def __init__(self,udp_ip,udp_port):
        # self.UDP_IP = udp_ip
        # self.UDP_PORT = udp_port
        # self.sock = socket.socket(socket.AF_INET, # Internet
        #                 socket.SOCK_DGRAM) # UDP
        # #self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
        self.socket_a = self.socket.define(BaseNamespace,'/JT601')
        self.socket_a.emit("joinWebsite")

        self.mavlink_queue = queue.Queue()

        # receive_thread = threading.Thread(target= self.receive_data, daemon = True)
        # receive_thread.start()

    def send_data(self,data):
        #self.sock.sendto(data,(self.UDP_IP,self.UDP_PORT))
        self.socket_a.emit("LAND",str(data))
        self.socket.wait(seconds=0.01)

    # def receive_data(self):
    #     while True:
    #         data,_ = self.sock.recvfrom(1024)
    #         self.mavlink_queue.put(data)


def do_mavlink_send(drone,check_gcs):
    while True:
        if 100 <= drone.in_waiting < 4095:  
            data = drone.read(drone.in_waiting)
            while data:
                print('[Drone -> Internet] {}'.format(data))
                #check_gcs.send_data(data[:255])
                #data = data[255:]
        elif drone.in_waiting == 4095:
            drone.reset_input_buffer()
        else:
            pass

# def do_mavlink_receive(drone,check_gcs):
#     while True:
#         while not check_gcs.mavlink_queue.empty():
#             drone.write(check_gcs.mavlink_queue.get())

def main():
    drone = serial.Serial('/dev/ttyACM0',115200)
    check_gcs = HandleServer(udp_ip=UDP_IP,udp_port=UDP_PORT)
    
    mavlink_send_thread = threading.Thread(target= do_mavlink_send, args = (drone,check_gcs,),daemon = True)
    mavlink_send_thread.start()
    
    # mavlink_rx_thread = threading.Thread(target=do_mavlink_receive,args=(drone,check_gcs,),daemon = True)
    # mavlink_rx_thread.start()

    input()



if __name__ == '__main__':
    main()