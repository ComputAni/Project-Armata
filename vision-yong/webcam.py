import cv2
import obstacleDetection
import os
import time

# knownDist, knownWidthPx = obstacleDetection.calibrateObstacle()
# print(knownDist, knownWidthPx)
# print(obstacleDetection.getDistance(knownDist, knownWidthPx, 'captured.jpg', 1))

camIndex = 0 # Default camera is at index 0.
cap = cv2.VideoCapture(camIndex) # Video capture object
cap.open(camIndex) # Enable the camera



def takeIm(cap, camIndex, filename):
    cnt = 0
    while True:
        _, frame = cap.read() # gets one frame from the webcam
        if frame is not  None:
            if cnt < 10:
                cnt += 1
            else:
                cv2.imwrite(filename, frame)
                break
        else:
            cap.release()
            cap = cv2.VideoCapture(camIndex)
    print("Done taking Image")

(knownDistance, knownWidthPx) = obstacleDetection.calibrateObstacle()
print (knownDistance, knownWidthPx)

if not os.access("captured", os.F_OK):
    os.mkdir("captured")

for i in range(1):
    print i
    filename = "captured" + os.sep + "im" + str(i) + "_test.png"
    takeIm(cap, camIndex, filename)
    distance = obstacleDetection.getDistance(knownDistance, knownWidthPx, filename, i)
    print "Distance" + str(distance)
    if distance > 15.0:
        pass
        #threadDrive.forward(motorL)
    else:
        print "Done"
cap.release()
#gpio.cleanup()

