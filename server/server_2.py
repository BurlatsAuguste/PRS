import socket
import threading


def send_file(port, step):
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.bind((UDP_IP, port))
    sock_client.settimeout(0.1)
    filename, address = sock_client.recvfrom(1024)
    print("received :", filename.decode('utf-8'))

    file = open(filename.decode('utf-8').rstrip('\0'), 'rb')

    content = file.read()

    i = 0
    NUM_SEQ = 1

    base_step = step
    end = 0
    previous_end = 0

    print("len = ", len(content))
    while end < len(content):
        end = previous_end + step if (previous_end + step) < len(content) else len(content)
        SEQ = bytes(str(NUM_SEQ).zfill(6), 'utf-8')
        SEQ += content[previous_end:end]
        # print("len :", len(SEQ) - 6)
        print("SEQ : ["+str(previous_end)+":"+str(end)+"]")
        sock_client.sendto(SEQ, address)
        try:
            data, address = sock_client.recvfrom(1024)
            print("received :", data.decode('utf-8'))
            if data.decode('utf-8').rstrip('\0') != "ACK" + str(NUM_SEQ).zfill(6):
                NUM_SEQ += -1
            else:
                i += 1
                NUM_SEQ += 1
                previous_end = end
                step = 2 * step if (2 * step) + 6 < 1500 else 1500 - 6
        except socket.timeout:
            print("no ACK received, trying sending again")
            previous_step = step
            step = base_step
            continue
    MESSAGE = bytes("FIN", 'utf-8')
    sock_client.sendto(MESSAGE, address)


if __name__ == "__main__":
    UDP_IP = "127.0.0.1"
    UDP_PORT = 16000

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

        thread = threading.Thread(target=send_file, args=(int(new_port), 16))
        thread.start()

        # SYN-ACK
        MESSAGE = bytes("SYN-ACK" + new_port, 'utf-8')
        sock.sendto(MESSAGE, addr)

        # ACK
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
