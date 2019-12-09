import socket
import threading


def send_file(port, step):
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.bind((UDP_IP, port))
    sock_client.settimeout(0.1)
    filename, address = sock_client.recvfrom(1024)
    print("received :", filename.decode('utf-8'))

    file = open('files/'+filename.decode('utf-8').rstrip('\0'), 'rb')

    content = file.read()

    i = 0
    NUM_SEQ = 1
    print("len = ", len(content))
    while i * step <= len(content):
        print("i = ", i)
        end = (i + 1) * step if (i + 1 * step) < len(content) else len(content)
        SEQ = bytes(str(NUM_SEQ).zfill(6), 'utf-8')
        SEQ += content[i * step:end]
        print("send : ", NUM_SEQ)
        sock_client.sendto(SEQ, address)
        try :
            data, address = sock_client.recvfrom(1024)
            print("received :", data.decode('utf-8'))
            if data.decode('utf-8').rstrip('\0') != "ACK"+str(NUM_SEQ).zfill(6):
                NUM_SEQ += -1
            else:
                i += 1
                NUM_SEQ += 1
        except socket.timeout:
            print("no ACK received, trying sending again")
            continue
        print("wesh")
    MESSAGE = bytes("FIN", 'utf-8')
    sock_client.sendto(MESSAGE, address)


if __name__ == "__main__":
    UDP_IP = ''
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    port = 2000

    while 1:
        # SYN
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
        new_port = str(port)
        port += 1

        thread = threading.Thread(target=send_file, args=(int(new_port), 1024))
        thread.start()

        # SYN-ACK
        MESSAGE = bytes("SYN-ACK" + new_port, 'utf-8')
        sock.sendto(MESSAGE, addr)

        # ACK
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
