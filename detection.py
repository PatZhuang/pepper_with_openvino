#!/usr/bin/python3
# requires python version >= 3.7

import sys
ros_cv2_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_cv2_path in sys.path:
    sys.path.remove(ros_cv2_path)

import cv2
import numpy as np
import socket

# download these files from 
# https://storage.openvinotoolkit.org/repositories/open_model_zoo/2021.3/models_bin/2/

face_model_xml = '/home/center/openvino_models/ir/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml'
face_model_bin = '/home/center/openvino_models/ir/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.bin'
person_model_xml = '/home/center/openvino_models/ir/intel/person-detection-retail-0013/FP16/person-detection-retail-0013.xml'
person_model_bin = '/home/center/openvino_models/ir/intel/person-detection-retail-0013/FP16/person-detection-retail-0013.bin'

DETECT_FACE = False
DETECT_PERSON = True

# read model

if DETECT_FACE:
    face_net = cv2.dnn.readNet(face_model_xml, face_model_bin)
    # specify target device
    face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
    face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

    face_input_blob = 'data'
    face_out_blob = 'detection_out'

if DETECT_PERSON:
    person_net = cv2.dnn.readNet(person_model_xml, person_model_bin)
    person_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
    person_net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

    person_input_blob = 'data'
    person_out_blob = 'detection_out'

font = cv2.FONT_HERSHEY_SIMPLEX

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
        frame = np.ascontiguousarray(np.frombuffer(data, np.uint8).reshape(h, w, 3))
        if DETECT_FACE:
            face_blob = cv2.dnn.blobFromImage(frame, size=(672, 382), ddepth=cv2.CV_8U)
            face_net.setInput(face_blob)
            out = face_net.forward()
            for detection in out.reshape(-1, 7):
                confidence = float(detection[2])
                xmin = int(detection[3] * frame.shape[1])
                ymin = int(detection[4] * frame.shape[0])
                xmax = int(detection[5] * frame.shape[1])
                ymax = int(detection[6] * frame.shape[0])
                if confidence > 0.5:
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))
                    cv2.putText(frame, 'FACE', (xmin, (ymin-10)), font, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

        if DETECT_PERSON:
            person_blob = cv2.dnn.blobFromImage(frame, size=(544, 320), ddepth=cv2.CV_8U)
            person_net.setInput(person_blob)
            out = person_net.forward()
            for detection in out.reshape(-1, 7):
                confidence2 = float(detection[2])
                xmin2 = int(detection[3] * frame.shape[1])
                ymin2 = int(detection[4] * frame.shape[0])
                xmax2 = int(detection[5] * frame.shape[1])
                ymax2 = int(detection[6] * frame.shape[0])

                if confidence2 > 0.6:
                    cv2.rectangle(frame, (xmin2, ymin2), (xmax2, ymax2), color=(0, 255, 0))
                    cv2.putText(frame, 'PERSON', (xmin2, ymin2-10), font, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('OpenVINO face detection', frame)
   
    # exit socket
    sock.sendall(bytearray('exit', 'ASCII'))

finally:
    print('closing socket')
    sock.close()
    
