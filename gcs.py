from digi.xbee.devices import XBeeDevice
import threading

PORT = "/dev/ttyUSB1"
BAUD_RATE = 9600

device = XBeeDevice(PORT, BAUD_RATE)
data_queue = []
count = 0

def string_man(data_queue):
                global count
                #index_end = data_queue.index('$ed@')
                #index_start = data_queue.index('$st@')
                
                parsed_data = ''
                for i in data_queue:
                    if(i != '$ed@') and  (i != '$st@'):
                        #print("i:",i)
                        parsed_data = parsed_data + i
                
                print(parsed_data)
                print("count = ",count,"\r\n")
                count += 1


def main():
    device.open()

    def data_receive_callback(xbee_message):
            message = xbee_message.data.decode()
            #print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
            #                         message))
            #message = xbee_message.data.decode()
            data_queue.append(message)
            if(message == '$ed@'):
                
                a = threading.Thread(target = string_man,args = (data_queue,))
                a.start()
                #thread.start_new_thread(send_data,("Send Data", 1))
                data_queue.clear()
            # print("data_queue:",data_queue)
            

    device.add_data_received_callback(data_receive_callback)    
    print("Waiting for data...\n")
    
    input()
    

                


if __name__ == '__main__':
    main()