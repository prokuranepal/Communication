from digi.xbee.devices import XBeeDevice,XBee64BitAddress,RemoteXBeeDevice
from socketIO_client_nexus import SocketIO, BaseNamespace
import threading
import json

PORT = "/dev/ttyUSB1"
BAUD_RATE = 57600

my_device = XBeeDevice(PORT, BAUD_RATE)
my_device.open()
data_queue = []
ADDRESS1 = "0013A200419B5AD8"
data_queue1 = ''
ADDRESS2 = "0013A20041554FF4"
data_queue2 = ''


count = 0
socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
# while not socket._connected:
#     socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)

socket_a = socket.define(BaseNamespace,'/JT601')
socket_a.emit("joinPi")

socket_b = socket.define(BaseNamespace,'/JT602')
socket_b.emit("joinPi")

def socket_function(parsed_data,drone):
    global count
    
    try:
        ini_string = json.dumps(parsed_data)
        processed_data = json.loads(ini_string)
        final_dictionary = eval(processed_data)
        #print(final_dictionary,"\n")
        print(count,"\n")
        count+=1
        drone.emit('data',final_dictionary)
    except Exception as e:
        print("error")
    socket.wait(seconds=0.2)



def string_man(data_queue,drone):
    global count

    parsed_data = data_queue.replace("$st@","")
    parsed_data = parsed_data.replace("$ed@","")
    print(parsed_data)

    b = threading.Thread(target = socket_function,args = (parsed_data,drone))
    b.start()
                

def send_data(address,message):
    remote_device = RemoteXBeeDevice(my_device, XBee64BitAddress.from_hex_string(address))
    my_device.send_data(remote_device , message)

def send_data_land_1(var):
    print("SET TO LAND")
    print(var)
    send_data(ADDRESS1,'LAND')

def send_data_rtl_1(var):
    print(var)
    print("Set to rtL")
    send_data(ADDRESS1,'RTL')
             
def main():
    def data_receive_callback(xbee_message):
        global data_queue1
        global data_queue2
        message = xbee_message.data.decode()
        address = str(xbee_message.remote_device.get_64bit_addr())
        
        if(address == ADDRESS1):
            data_queue1 += message
            if(message == '$ed@'):
                a = threading.Thread(target = string_man,args = (data_queue1,socket_a))
                a.start()
                data_queue1 = ''

        elif address == ADDRESS2:
            data_queue2     += message
            if(message == '$ed@'):
                b = threading.Thread(target = string_man,args = (data_queue2,socket_b))
                b.start()
                data_queue2 = ''

    my_device.add_data_received_callback(data_receive_callback)

    socket_a.on('LAND',send_data_land_1)
    #socket_b.on('LAND',send_data_land)
    socket_a.on('RTL',send_data_rtl_1)
    #socket_b.on('RTL',send_data(ADDRESS2,'RTL'))

    print("Waiting for data...\n")
    
    input()
    

                


if __name__ == '__main__':
    main()