import socket
import threading


def send_file(port, step):
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.bind((UDP_IP, port))

    filename, address = sock_client.recvfrom(1024)
    print("received :", filename.decode('utf-8'))

    file = open(filename.decode('utf-8'), 'r')

    content = file.read()

    i = -1
    MESSAGE = bytes(content, 'utf-8')
    NUM_SEQ = 1
    while i * 6 <= len(content):
        i += 1
        end = (i + 1) * step if (i + 1 * step) < len(content) else len(content)
        SEQ = bytes(str(NUM_SEQ).zfill(6) + MESSAGE[i * step:end].decode('utf-8'), 'utf-8')
        sock_client.sendto(SEQ, address)

        data, address = sock_client.recvfrom(1024)
        print("received :", data.decode('utf-8'))
        while data.decode('utf-8') != "ACK"+str(NUM_SEQ).zfill(6):
            sock_client.sendto(SEQ, address)
            data, address = sock_client.recvfrom(1024)
            print("received :", data.decode('utf-8'))
        NUM_SEQ += 1
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

        thread = threading.Thread(target=send_file, args=(int(new_port), 8))
        thread.start()

        # SYN-ACK
        MESSAGE = bytes("SYN-ACK" + new_port, 'utf-8')
        sock.sendto(MESSAGE, addr)

        # ACK
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
