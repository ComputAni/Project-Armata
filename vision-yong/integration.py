import cv2
import obstacleDetection
import threadDrive2
import RPi.GPIO as gpio

knownDist, knownWidthPx = obstacleDetection.calibrateObstacle()
print(knownDist, knownWidthPx)

# gpio.setmode(gpio.BOARD)
# threadDrive2.forward(1000)
# gpio.cleanup()

camera = cv2.VideoCapture(0)
_, image = camera.read()
cv2.imwrite('captured.jpg', image)

