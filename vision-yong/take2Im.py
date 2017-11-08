import cv2

cap = cv2.VideoCapture() # Video capture object
cap.open(0) # Enable the camera

def takeIm(cap, camIndex, filename):
    cnt = 0
    while True:
        _, frame = cap.read() # gets one frame from the webcam
        if frame is not  None:
            if cnt < 20:
                cnt += 1
            else:
                cv2.imwrite(filename, frame)
                break
        else:
            cap.release()
            cap = cv2.VideoCapture()
            cap.open(0)
    cap.release()
    print("Done taking Image")


takeIm(cap, 0, "im0.png")
