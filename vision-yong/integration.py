import cv2
import obstacleDetection
import threadDrive
import RPi.GPIO as gpio

# knownDist, knownWidthPx = obstacleDetection.calibrateObstacle()
# print(knownDist, knownWidthPx)
gpio.setmode(gpio.BOARD)
a = threadDrive.motor(3, 5, 40, 16)
b = threadDrive.motor(7, 11, 18, 22)
c = threadDrive.motor(15, 13, 26, 24)
d = threadDrive.motor(21, 19, 36, 32)
motorL = [a, b, c, d]
threadDrive.ccw(motorL)
threadDrive.forward(motorL)
threadDrive.cw(motorL)
for i in range(4):
    threadDrive.forward(motorL)
threadDrive.cw(motorL)
threadDrive.forward(motorL)
gpio.cleanup()

# print(obstacleDetection.getDistance(knownDist, knownWidthPx, 'captured.jpg', 1))
