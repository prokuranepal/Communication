import socket

UDP_IP = "127.0.0.1"

UDP_PORT_RX = 14550
UDP_PORT_TX = 14555

sock_rx = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock_rx.bind((UDP_IP, UDP_PORT_RX))

sock_tx = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM)


while True:
    data, addr = sock_rx.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)
    sock_tx.sendto(data,(UDP_IP,UDP_PORT_TX))
