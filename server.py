#!/usr/bin/python
import socket
import sys
import os

server_address = './uds_socket'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)   # delete socket file
except OSError:
    if os.path.exists(server_address):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# Bind the socket to the port
print('starting up on %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # wait for a connection
    print('Waiting for a connection.')
    connection, client_address = sock.accept()
    try:
        print('connection from %s' % client_address)
        # Receive the data in small chunks and retrainsmit is
        while True:
            data = connection.recv(16)
            print('received %s' % data)
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no more data from %s' % client_address)
                break
    finally:
        connection.close()