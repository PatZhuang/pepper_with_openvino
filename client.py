import socket
import sys
import cv2
import numpy as np
import time

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = './uds_socket'
print('connecting to %s' % server_address)

try:
    sock.connect(server_address)
except socket.error as e:
    print(e)
    sys.exit(1)

try:
    image_size = sock.recv(16).decode('ASCII')
    w, h, c = [int(d) for d in image_size.split('x')]
    data_len = w * h * c
    print('image size: (%d, %d, %d)' % (w, h, c))
    
    # cnt = 0
    # t0 = time.time()
    while cv2.waitKey(1) < 0:
        # send status to server
        sock.sendall(bytearray('ok', 'ASCII'))
        # colect image bytes data
        data = b''
        while len(data) < data_len:
            data += sock.recv(data_len)
        # decode image
        image = np.frombuffer(data, np.uint8).reshape(h, w, 3)[...,::-1]
        cv2.imshow('hello', image)
    #     cnt += 1
    # print(cnt/(time.time() - t0))

    # exit socket
    sock.sendall(bytearray('exit', 'ASCII'))

finally:
    print('closing socket')
    sock.close()