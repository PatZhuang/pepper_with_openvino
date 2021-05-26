#!/usr/bin/python
# requires python version >= 2.6 < 3, which should be 2.7

import qi
import argparse
import sys
import time
import Image
import socket
import os


def init_socket(server_address='./uds_socket'):
    server_address = server_address
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
    return sock


def send_img(sock, img):
    """
    Send image to socket client. 
    Image is a naoImage, so img[0], img[1], img[3] respond to width, height, channels
    and img[6] contains img data as ASCII chars
    """
    print('Waiting for a connection.')
    while True:
        connection, client_address = sock.accept()
        try:
            while True:
                print('sending image to client.')
                connection.sendall(img[6])
        finally:
            connection.close()


def main(session):
    # Get the service ALVideoDevice
    
    video_service = session.service("ALVideoDevice")
    resolution = 2	# check image_size for resolution, max is 3. 2 is recommended.
    colorSpace = 11	# RGB

    image_size = ['320x240x3', '640x480x3', '1280x960x3']
    
    videoClient = video_service.subscribe("get_image", resolution, colorSpace, 5)

    # init socket
    sock = init_socket()
    sock.listen(1)
    connection, client_address = sock.accept()

    # inform client about image size
    connection.sendall(bytes(image_size[resolution - 1]))

    while True:
        # check client status
        status = connection.recv(16)
        if status == b"exit":
            print('exit')
            break

        # Get a camera image
        # Image[6] contains the image data passed as an array of ASCII chars
        naoImage = video_service.getImageRemote(videoClient)
        w = naoImage[0]
        h = naoImage[1]
        img = naoImage[6]
        connection.sendall(img)
    
    connection.close()
    video_service.unsubscribe(videoClient)


def show_image():
    video_service = session.service("ALVideoDevice")
    resolution = 3	# check image_size for resolution, max is 3
    colorSpace = 11	# RGB

    image_size = ['320x240x3', '640x480x3', '1280x960x3']
    
    videoClient = video_service.subscribe("get_image", resolution, colorSpace, 5)
    
    t0 = time.time()
    # Get a camera image
    # Image[6] contains the image data passed as an array of ASCII chars
    naoImage = video_service.getImageRemote(videoClient)
    t1 = time.time()
    print("delay: %.2f" % (t1 - t0))

    w = naoImage[0]
    h = naoImage[1]
    img = naoImage[6]

    video_service.unsubscribe(videoClient)

    img_str = str(bytearray(img))

    # Create a PIL image from pixel array
    im = Image.frombytes('RGB', (w, h), img_str)
    print(type(im))
    print("image of (%d x %d)" %(w, h))

    # save image and show
    im.save("test.png", "PNG")
    im.show()

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.64.26", help="Robot IP address.")
    parser.add_argument("--port", type=int, default=9559, help="Naoqi port number.")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print("Cannot connect to Naoqi at ip %s on port %d. Please check your arguments." %(args.ip, args.port))
        sys.exit(1)
    main(session)
