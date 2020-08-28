import socket
from socketIO_client_nexus import SocketIO, BaseNamespace
import json

def receive_data(var):
    print(var)

socket = SocketIO('https://nicwebpage.herokuapp.com', verify =True)
socket_a = socket.define(BaseNamespace,'/JT601')
socket_a.emit("joinPi")
print("conected to server")


while True:
    socket_a.on("LAND",receive_data)
    #socket_a.emit("homePosition",i)
    socket.wait(seconds=0.01)
