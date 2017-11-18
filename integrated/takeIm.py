import cv2
import sys

#cap = cv2.VideoCapture() # Video capture object
#cap.open(0) # Enable the camera

def takeIm(cap, camIndex, filename):

    cnt = 0
    while True:
        _, frame = cap.read() # gets one frame from the webcam
        if frame is not  None:
            if cnt < 15:
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

    return

# if len(sys.argv) < 2:
#     print("Need number in cmdline argument for filename!")
# else:
#     takeIm(cap, 0, "im" + str(sys.argv[1]) + ".png")

#takeIm(cap, 0, "im" + str(sys.argv[1]) + ".png")

