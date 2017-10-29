import cv2
from obstacleDetection import *
import threadDrive2

knownDist, knownWidthPx = calibrateObstacle()
print(knownDist, knownWidthPx)
