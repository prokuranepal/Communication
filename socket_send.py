# import json
# import socket
# UDP_IP = "127.0.0.1"
# UDP_PORT = 14550
# MESSAGE = b"Hello, World!"

# sock = socket.socket(socket.AF_INET,  # Internet
#                      socket.SOCK_DGRAM)  # UDP
# while True:
#     sock.sendto(json.dumps({'command': 'summary'}), (UDP_IP, UDP_PORT))

import socket
import pickle


class ProcessData:
    process_id = 0
    project_id = 0
    task_id = 0
    start_time = 0
    end_time = 0
    user_id = 0
    weekend_id = 0


HOST = 'localhost'
PORT = 14550
# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Create an instance of ProcessData() to send to server.
variable = ProcessData()
# Pickle the object and send it to the server
data_string = pickle.dumps(variable)
s.send(data_string)

s.close()
