# Adapted largely from http://cbarker.net/opencv/

import time
import cv2

cam_index = 0 # Default camera is at index 0.
cap = cv2.VideoCapture(cam_index) # Video capture object


cap.open(cam_index) # Enable the camera
frame = None
while True:
    _, frame = cap.read() # gets one frame from the webcam
    if frame is not  None:
        cv2.imwrite('captured.jpg', frame)
        break
    else:
        cap.release()
        cap = cv2.VideoCapture(cam_index)

cap.release()

