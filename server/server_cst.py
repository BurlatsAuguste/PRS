import socket
import threading
import time
from sys import argv
from math import floor


def listen(sock_client, ACK_tab):
    while(1):
        #we listen the socket to receive ACKs
        data_ack, address = sock_client.recvfrom(1024)
        print("received :", data_ack.decode('utf-8'))
        message = data_ack.decode('utf-8').rstrip('\0')
        index = int(message[3::])
        for i in range(index):
            ACK_tab[i][0] += 1


def send_file(socket_port, packet_length):
    # socket initialization
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.bind((UDP_IP, socket_port))

    RTT = 0.05
    cwnd = 10 #window size
    Tab_ACK = []

    # file initialization
    filename, address = sock_client.recvfrom(1024)
    print("received :", filename.decode('utf-8'))
    file = open('files/' + filename.decode('utf-8').rstrip('\0'), 'rb')
    content = file.read()
    step = 0
    NUM_SEG = 1  # the number of the segment

    # loop where we send the file in packets of <packet_length> length
    while step * packet_length <= len(content):
        # we adapt the end of the sequence to the length of the content in order not to send random
        # data from the memory
        end = (step + 1) * packet_length if (step + 1 * packet_length) < len(content) else len(content)

        # we create the segment number on 6 bytes then we add the content of the file
        SEG = bytes(str(NUM_SEG).zfill(6), 'utf-8')
        SEG += content[step * packet_length:end]
        Tab_ACK.append([0, 0, SEG, 0]) #[nbr of received ACK for this segment, time when we send the segment, segment number, did we already send the segment once]
        NUM_SEG +=1
        step += 1

    #we start a thread to listen the socket
    thread = threading.Thread(target=listen, args=(sock_client, Tab_ACK))
    thread.start()
    Last_Segment = False
    NUM_SEG = 1


    while(NUM_SEG < len(Tab_ACK) and Last_Segment == 0):
        #if we received the ACK of the first window's packet we slice the window
        while(Tab_ACK[NUM_SEG - 1][0] > 0 and NUM_SEG < len(Tab_ACK)):
            NUM_SEG += 1

        #we run through the window to launch the segments
        for i in range(int(cwnd)):
            if((i+NUM_SEG) > len(Tab_ACK)):
                break

            #If one segment has never been sent we send it
            if(Tab_ACK[i+NUM_SEG - 1][3] == 0):
                print("send : ", i+NUM_SEG)
                sock_client.sendto(Tab_ACK[i+NUM_SEG-1][2], address)
                Tab_ACK[i+NUM_SEG-1][3] += 1
                Tab_ACK[i+NUM_SEG-1][1] = time.time()

                #if we detect a loss we resend the lost segment
            elif((Tab_ACK[i+NUM_SEG - 1][0] == 0) and ((time.time() - Tab_ACK[i+NUM_SEG-1][1] > RTT) or (Tab_ACK[i+NUM_SEG-2][0] > 3 and Tab_ACK[i+NUM_SEG-1][3] < 2))):
                print("loss detected")
                print("send : ", i+NUM_SEG)
                sock_client.sendto(Tab_ACK[i+NUM_SEG-1][2], address)
                Tab_ACK[i+NUM_SEG-1][1] = time.time()
                Tab_ACK[i+NUM_SEG-1][3] += 1

        #if we received an ACK for the last segment, that means we reached the end
        Last_Segment = Tab_ACK[len(Tab_ACK) - 1][0]

    # when we reach the end of the content we send a message "FIN" to the client to end the communication
    MESSAGE_FIN = bytes("FIN", 'utf-8')
    for i in range(10):
        sock_client.sendto(MESSAGE_FIN, address)
    thread.join()


if __name__ == "__main__":
    # initialization of the arguments from the command line
    if len(argv) < 2:
        print("Use of the program : 'python3 " + argv[0] + " <port number>'")
        exit(1)

    if int(argv[1]) <= 1000:
        print("The port number must be above 1000")
        exit(1)

    port = int(argv[1])

    # we listen to every interfaces on port given by args on the console
    UDP_IP = ''
    UDP_PORT = port

    # socket initialization
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    # we give a new port to send the file that's above the original port
    port_new = port + 1 if port + 1 < 65535 else 1001

    #
    while 1:
        # receiving the SYN from the client
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
        port_new = port_new + 1 if port_new + 1 < 65535 else 1001

        # we start the thread before sending the SYN-ACK because the thread can take too much time to start
        # and the client try to connect to a socket that does not exist yet, causing an error
        thread = threading.Thread(target=send_file, args=(int(port_new), 1494))
        thread.start()

        # sending the SYN-ACK to the client with the new port number
        MESSAGE = bytes("SYN-ACK" + str(port_new), 'utf-8')
        sock.sendto(MESSAGE, addr)

        # receiving ACK from the client
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
