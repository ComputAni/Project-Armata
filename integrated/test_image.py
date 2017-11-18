from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
 
 # initialize the camera and grab a reference to the raw camera capture

def takeIm(file_name):
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
      
    # allow the camera to warmup
    time.sleep(0.1)
       
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array

    img = cv2.resize(image, (0,0), fx = 0.5, fy = 0.5, interpolation = cv2.INTER_AREA);

    # display the image on screen and wait for a keypress
    cv2.imwrite(file_name, img)

# takeIm("calibrate.png")
