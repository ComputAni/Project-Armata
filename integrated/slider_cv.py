# webcam functionality adapted largely from http://cbarker.net/opencv/
# slider setup from: https://botforge.wordpress.com/2016/07/02/basic-color-tracker-using-opencv-python/
# and: http://docs.opencv.org/2.4/modules/highgui/doc/user_interface.html

import cv2
import numpy as np

def findPoints(cnt):
    total = []
    allArrays = []
    if len(cnt) > 0:
        for array in cnt:
            total.append(cv2.contourArea(array))
            allArrays.append(array)
        # Below, finds bounding rectangles of all contours that are greater than area 5000
        return [cv2.boundingRect(allArrays[i]) for i in range(len(allArrays)) if total[i] > 5000]
    else:
        return []

#dummy callback function for cv2.createTrackbar()
def nothing(temp):
    return

def boundingRect():

    rgbMax = 255
    rgbMin = 0

    sliderWinName = 'ThreshSliders'
    cv2.namedWindow(sliderWinName)

    cam_index = 0 # Default camera is at index 0.
    cap = cv2.VideoCapture(cam_index) # Video capture object

    sliders = ['H_MAX', 'S_MAX', 'V_MAX', 'H_MIN', 'S_MIN', 'V_MIN']

    #initialize sliders
    for slider in sliders:
        cv2.createTrackbar(slider, sliderWinName, rgbMin, rgbMax, nothing)
    for slider in sliders[0:3]:
        cv2.setTrackbarPos(slider, sliderWinName, rgbMax)

    cap.open(cam_index) # Enable the camera
    while True:
        
        # ret, frame = cap.read() # gets one frame from the webcam
        frame = cv2.imread("im0.png")

        #collect threshold values from sliders (set by user)
        thresholds = []
        for slider in sliders:
            thresholds.append(cv2.getTrackbarPos(slider, sliderWinName))

        upperBound = np.array(thresholds[0:3])
        lowerBound = np.array(thresholds[3:6])

        #read more about hsv here: http://docs.opencv.org/3.2.0/df/d9d/tutorial_py_colorspaces.html
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        threshold = cv2.inRange(hsv, lowerBound, upperBound)

        _, contours, hierarchy = cv2.findContours(threshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        rectL = findPoints(contours)

        for rect in rectL:
            x, y, w, h = rect 
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),5)

        cv2.imshow('Thresh', threshold)
        cv2.imshow('CamInput', frame)

        #closes all windows and exits when escape key is pressed
        k = cv2.waitKey(10) & 0xFF
        if k == 27: # code for escape key
            cv2.destroyAllWindows()
            cap.release()
            break

boundingRect()
