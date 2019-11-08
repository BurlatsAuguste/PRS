import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

# region 3 way handshake
# SYN
MESSAGE = bytes("SYN", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# SYN-ACK
data, addr = sock.recvfrom(1024)
rcv = data.decode('utf-8')
print("received message:", rcv)

new_port = int(rcv[-4:])
print("new port :", new_port)

# ACK
MESSAGE = bytes("ACK", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# endregion

# region receiving file
MESSAGE = bytes("fanfiction.txt", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, new_port))

data, addr = sock.recvfrom(1024)
rcv = data.decode('utf-8')
print("received message:", rcv)
# endregion
