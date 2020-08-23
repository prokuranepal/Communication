import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 14550
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)

# import socket
# import pickle


# class ProcessData:
#     process_id = 0
#     project_id = 0
#     task_id = 0
#     start_time = 0
#     end_time = 0
#     user_id = 0
#     weekend_id = 0


# HOST = 'localhost'
# PORT = 14550
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen(1)

# # Access the information by doing data_variable.process_id or data_variable.task_id etc..,
# # print 'Data received from client'
# while True:
#     conn, addr = s.accept()
#     # print 'Connected by', addr
#     data = conn.recv(4096)
#     data_variable = pickle.loads(data)
#     conn.close()
#     print(data_variable)
