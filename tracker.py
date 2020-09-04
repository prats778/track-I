######----------- ---- --   Team trac-i  -- ---- ------------######
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import time
import argparse
import numpy as np
import imutils
import cv2
import dlib
import os
import time
from datetime import datetime

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)
    return ear

def get_file_name(time_stamp):
    date = str(datetime.fromtimestamp(timestamp))
    date = date.split(" ")
    tym = date[1].split(":")
    tym = tym[0]+"-"+tym[1]+"-"+tym[2]
    date = date[0]+"x"+tym+".txt"
    return date    

EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

COUNTER = 0
TOTAL = 0

print('[INFO] Loading facial landmark predictor...')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.path.join(os.getcwd(), "shape_predictor_68_face_landmarks.dat"))

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

print('[INFO] Starting video stream thread...')
fileStream = False
vs = VideoStream(src=0).start()
fileStream = False

time.sleep(1.0)

start = time.time()
program_start = start
stop, prev, curr = 0.0, 0.0, 0.0
stop_flag = False
last_tym = 0

# storage space ---------------------------
storage_path = os.path.join(os.getcwd(), "database" )
timestamp = int(start)
file_name = get_file_name(timestamp)
fs = open(os.path.join(storage_path, file_name), 'w+')

fs.write("STARTED AT "+str(program_start)+"\n")

while True:
    if fileStream and not vs.more():
        break

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)
    flag = 0
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart: lEnd]
        rightEye = shape[rStart: rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1

            COUNTER = 0
        
        
        cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        flag = 1
        
    diff = time.time() - start
    start = time.time()
    
    if(flag):
        if(stop_flag and int(stop)>1):
            fs.write("STOPPED FOR "+str(int(stop))+"\n")
            stop_flag = False
        curr += diff
        stop = 0
        if( (int(curr)%10 == 0) and last_tym!=(int(curr)) ):
            fs.write(str(int(curr))+" "+str(TOTAL)+"\n")
            last_tym = int(curr)
    else:
        stop += diff
        stop_flag = True
        

    cv2.putText(frame, "Time: {:.2f}".format(curr), (140, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

fs.write("STOPPED AT "+str(time.time())+"\n")
fs.close()
cv2.destroyAllWindows()
vs.stop()
