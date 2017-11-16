import numpy as np
import cv2
import copy

# Find the obstacle in the image
def findObject(image, count):

	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	#color = np.uint8([[[196, 114, 68]]])
	color = np.uint8([[[100, 81, 54]]])
	#color = np.uint8([[[159, 88, 183]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
	hue = hsv_color[0][0][0]

	lower_range = np.array([hue-100, 50, 50], dtype=np.uint8)
	upper_range = np.array([hue+100, 225, 225], dtype=np.uint8)

	mask = cv2.inRange(hsv, lower_range, upper_range)
	#mask = cv2.inRange(hsv, hsv_color, hsv_color)
        fileName = "results/mask" + str(count) + ".png"
	cv2.imwrite(fileName, mask)

	gray = cv2.GaussianBlur(mask, (9, 9), 0)
	edged = cv2.Canny(gray, 50, 150)
	
	# Save the edges image for debugging purposes
	fileName = "results/edged" + str(count) + ".png"
	cv2.imwrite(fileName, edged)

	
	# find the contours in the edged image and keep the largest one;
	# we'll assume that this is our piece of paper in the image
	(_,cnts,hierarchy) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	
	mask = cv2.drawContours(mask, cnts, -1, (0,255,0), 3)

	fileName = "results/findMarker" + str(count) + ".png"
	cv2.imwrite(fileName, mask)

	maxPerimeter = 0
	mainCnt = None
	
	# Find the contour with the largest perimeter
	for cnt in cnts:
		perimeter = cv2.arcLength(cnt, True)
		approx = cv2.approxPolyDP(cnt, 0.005 * perimeter, True)

		area = cv2.contourArea(cnt)

		# Get the contour with the largest perimeter that has 4 sides
		#if (len(approx) == 4) and (perimeter > maxPerimeter):
		
		if(area > maxPerimeter):
			maxPerimeter = area
			mainCnt = cnt			
		# if (perimeter > maxPerimeter):
		# 	maxPerimeter = perimeter
		# 	mainCnt = cnt

	# compute the bounding box of the of the paper region and return it
	return cv2.minAreaRect(mainCnt)

# Assuming that the right bounding box was found, sort the points and find the top left and top right points.
def sortPoints(box):

	y = []

	top = []
	
	for i in xrange(len(box)):
		y.append(box[i][1])

	yMean = sum(y) / len(y)

	for i in xrange(len(box)):

		if (box[i][1] < yMean):
			top.append(box[i])

	topLeft = ()
	topRight = ()

	if top[0][0] < top[1][0]:
		topLeft = top[0]
		topRight = top[1]
	else:
		topLeft = top[1]
		topRight = top[0]


	return topRight[0] - topLeft[0]


# Get the distance given 
def distance_to_camera(knownDistance, knownWidthPx, width):
	# compute and return the distance from the maker to the camera
	return (knownWidthPx / width) * knownDistance
 
# initialize the known distance from the camera to the object, which
# in this case is 24 inches

def calibrateObstacle():
	knownDistance = 24
	image = cv2.imread('robotObstacle/obstacleCalibrate.png')
	marker = findObject(image, 0)
	box = np.int0(cv2.boxPoints(marker))
	knownwidthPx = sortPoints(box)


	return (knownDistance, knownwidthPx)

def getDistance(knownDistance, knownWidthPx, imagePath, count):

	image = cv2.imread(imagePath)
	
	# Find the obstacle of the image
	marker = findObject(image, count)
 
	# draw a bounding box around the image and display it
	box = np.int0(cv2.boxPoints(marker))
	widthPx = sortPoints(box)

	inches = distance_to_camera(knownDistance, knownWidthPx*1.0, widthPx*1.0)

	cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
	cv2.putText(image, "%finches" % (inches),
		(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
		2.0, (0, 255, 0), 3)
	# cv2.imshow("image", image)
	# cv2.waitKey(0)
	fileName = "results/distance" + str(count) + ".png"
	cv2.imwrite(fileName, image)

	return inches

#knownDistance, knownWidthPx = calibrateObstacle()

IMAGE_PATHS = ['obstacle12.png', 'obstacle15.png', 'obstacle24.png', 'obstacle30.png', 'obstacle36.png', 'obstacle48.png', 'obstacle60.png', 'obstacle72.png', 'obstacle84.png']
count = 1

# loop over the images
#for imagePath in IMAGE_PATHS:
	# load the image, find the marker in the image, then compute the
	# distance to the marker from the camera
	
#	print getDistance(knownDistance, knownWidthPx, "robotObstacle/" + imagePath, count)

#	count += 1


'''
1. Experimentally determine ratio of x-displacement to depth (R)
(ie for specific depth d, and world coord x-displacement to reach edge of screen x
R = x / d)
2. For new depth D, the edge of the screen is X units away where X = D * R
3. Assuming linear relationship between world coord and screen space
the x-displacement of the centroid is X * (centroid_x_im / im_width)
'''
def getXcoord(depth, xPix):
	xDepthRatio = 13.7 / 34 # Experimental ratio of x displacement to depth (world coord)
	halfScreenW = 320
	return xDepthRatio * depth * (xPix / float(halfScreenW))

