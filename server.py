import socket
import threading


def send_file(port):
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.bind((UDP_IP, port))

    filename, address = sock_client.recvfrom(1024)
    print("received :", filename.decode('utf-8'))

    MESSAGE = bytes("sending...", 'utf-8')
    sock_client.sendto(MESSAGE, address)


if __name__ == "__main__":
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while 1:
        # SYN
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
        new_port = str(5006)

        thread = threading.Thread(target=send_file, args=(5006,))
        thread.start()

        # SYN-ACK
        MESSAGE = bytes("SYN-ACK" + new_port, 'utf-8')
        sock.sendto(MESSAGE, addr)

        # ACK
        data, addr = sock.recvfrom(1024)
        print("received :", data.decode('utf-8'))
