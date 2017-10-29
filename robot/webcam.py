# Adapted largely from http://cbarker.net/opencv/

import time
import cv2

window_name = "Webcam!"
cam_index = 0 # Default camera is at index 0.
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(cam_index) # Video capture object


cap.open(cam_index) # Enable the camera
for i in range(10):
    ret, frame = cap.read() # gets one frame from the webcam
    if frame is not None:
        # Resizing the frame! Ignore dsize. fx scales the width, fy scales the height
        frame = cv2.resize(frame, dsize=(0,0), fx=1.5,fy=1.5)
        cv2.imshow(window_name, frame)
    if i == 9:
        cv2.imwrite('captured.jpg', frame)
