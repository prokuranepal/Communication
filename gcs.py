from digi.xbee.devices import XBeeDevice
from socketIO_client_nexus import SocketIO, BaseNamespace
import threading
import json

PORT = "/dev/ttyUSB1"
BAUD_RATE = 57600

device = XBeeDevice(PORT, BAUD_RATE)

data_queue = []
ADDRESS1 = "0013A200419B5AD8"
data_queue1 = ''
ADDRESS2 = "0013A20041554FF4"
data_queue2 = ''


count = 0
socket1 = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
socket = socket1.define(BaseNamespace,'/JT601')
while not socket._connected:
    socket1 = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
    socket = socket1.define(BaseNamespace,'/JT601')
socket.emit("joinPi")

def socket_function(parsed_data):
    global count
    try:
        ini_string = json.dumps(parsed_data)
        processed_data = json.loads(ini_string)
        final_dictionary = eval(processed_data)
        #print(final_dictionary,"\n")
        print(count,"\n")
        count+=1
        socket.emit('data',final_dictionary)
    except Exception as e:
        print("error")
    socket1.wait(seconds=0.2)



def string_man(data_queue):
                global count
                #index_end = data_queue.index('$ed@')
                #index_start = data_queue.index('$st@')
                parsed_data = data_queue.replace("$st@","")
                parsed_data = parsed_data.replace("$ed@","")
                print(parsed_data)
                # parsed_data = ''
                # for i in data_queue:
                #     if(i != '$ed@') and  (i != '$st@'):
                #         #print("i:",i)
                #         parsed_data = parsed_data + i
                
                #print( parsed_data,"\n")
                
                #b = threading.Thread(target = socket_function,args = (parsed_data,))
                #b.start()git
                
             
def main():
    
    device.open()
    def data_receive_callback(xbee_message):
            global data_queue1
            global data_queue2
            message = xbee_message.data.decode()
            address = str(xbee_message.remote_device.get_64bit_addr())
            #print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
            #                         message))
            #message = xbee_message.data.decode()
            #msg_dict = {}
            #msg_dict['id']= address
            #print(type(address))
            if(address == ADDRESS1):
                #print("Here")

                data_queue1 += message
                if(message == '$ed@'):
                    b = threading.Thread(target = string_man,args = (data_queue1,))
                    b.start()
                    # thread.start_new_thread(send_data,("Send Data", 1))
                    data_queue1 = ''
            elif address == ADDRESS2:
                data_queue2 += message
                if(message == '$ed@'):
                    a = threading.Thread(target = string_man,args = (data_queue2,))
                    a.start()
                    # thread.start_new_thread(send_data,("Send Data", 1))
                    data_queue2 = ''
            #data_queue.append(message)
            # print(data_queue)
            # if(message == '$ed@'):
            #     a = threading.Thread(target = string_man,args = (data_queue,))
            #     a.start()
            #     # thread.start_new_thread(send_data,("Send Data", 1))
            #     data_queue.clear()
            # # print("data_queue:",data_queue)
            

    device.add_data_received_callback(data_receive_callback)    
    print("Waiting for data...\n")
    
    input()
    

                


if __name__ == '__main__':
    main()