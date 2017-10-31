import cv2
import obstacleDetection
import threadDrive
import RPi.GPIO as gpio
import os

# knownDist, knownWidthPx = obstacleDetection.calibrateObstacle()
# print(knownDist, knownWidthPx)
# print(obstacleDetection.getDistance(knownDist, knownWidthPx, 'captured.jpg', 1))

camIndex = 0 # Default camera is at index 0.
cap = cv2.VideoCapture(camIndex) # Video capture object
cap.open(camIndex) # Enable the camera

def takeIm(cap, camIndex, filename):
    while True:
        _, frame = cap.read() # gets one frame from the webcam
        if frame is not  None:
            cv2.imwrite(filename, frame)
            break
        else:
            cap.release()
            cap = cv2.VideoCapture(camIndex)

if not os.access("captured", os.F_OK):
    os.mkdir("captured")

gpio.setmode(gpio.BOARD)
a = threadDrive.motor(3, 5, 40, 16)
b = threadDrive.motor(7, 11, 18, 22)
c = threadDrive.motor(15, 13, 26, 24)
d = threadDrive.motor(21, 19, 36, 32)
motorL = [a, b, c, d]

for i in range(3):
    filename = "captured" + os.sep + "im" + str(i) + "_test.jpg"
    takeIm(cap, camIndex, filename)
    threadDrive.forward(motorL)

cap.release()
gpio.cleanup()

