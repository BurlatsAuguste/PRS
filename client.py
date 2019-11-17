import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 16000

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

# region 3 way handshake
# SYN
MESSAGE = bytes("SYN", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# SYN-ACK
data, addr = sock.recvfrom(1024)
rcv = data.decode('utf-8')
print("received :", rcv)

new_port = int(rcv[-4:])
print("new port :", new_port)

# ACK
MESSAGE = bytes("ACK", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# endregion

# region receiving file
MESSAGE = bytes("fanfic.txt", 'utf-8')
sock.sendto(MESSAGE, (UDP_IP, new_port))
file = ""
while data.decode('utf-8') != "FIN":
    data, addr = sock.recvfrom(1024)
    rcv = data.decode('utf-8')
    SEQ_NUM = rcv[:6]
    MESSAGE = bytes("ACK"+SEQ_NUM, 'utf-8')
    sock.sendto(MESSAGE, (UDP_IP, new_port))
    file += rcv[6:] if rcv != "FIN" else ""
print(file)
# endregion
