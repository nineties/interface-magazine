from mpu6050 import MPU6050
import time
import struct
import socket

sensor = MPU6050()

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(('0.0.0.0', 9000))
server_sock.listen(1)

while True:
    client_sock, client_addr = server_sock.accept()
    print 'Connected from {}'.format(client_addr)

    try:
        start = time.time()
        while True:
            t = time.time() - start
            data = sensor.get()
            client_sock.send(struct.pack('7f', t, *data))
    except socket.error:
        print 'Disconnected'
