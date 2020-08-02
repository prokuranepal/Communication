from digi.xbee.devices import XBeeDevice

PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

device = XBeeDevice(PORT, BAUD_RATE)
def main():
    device.open()

    def data_receive_callback(xbee_message):
            print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
                                     xbee_message.data.decode()))

    device.add_data_received_callback(data_receive_callback)

    print("Waiting for data...\n")
    input()

if __name__ == '__main__':
    main()