# Sources: 
# 1) https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_matcher/py_matcher.html#matcher
# 2) https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html#py-feature-homography
# 3) https://www.pyimagesearch.com/2015/07/16/where-did-sift-and-surf-go-in-opencv-3/ - To install openCV-contrib packages to get access to patented algos such as SIFT

import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 20


# # Need to draw only good matches, so create a mask
# matchesMask = [[0,0] for i in xrange(len(matches))]

# # ratio test as per Lowe's paper
# for i,(m,n) in enumerate(matches):
#     if m.distance < 0.7*n.distance:
#         matchesMask[i]=[1,0]

def removePoints(im, pxToRemove):

	box = []
	for i in xrange(len(pxToRemove)):
		px = pxToRemove[i][0]
		#print px, len(px)
		x = px[0]
		y = px[1]

		box.append([int(round(x)), int(round(y))])


	l = list()
	l.append(box)

	finalBox = np.array(l, dtype=np.int32)

	cv2.fillPoly(im, finalBox, 255)

	return im, box

def sortPoints(box):

	y = []

	top = []
	
	for i in xrange(len(box)):
		y.append(box[i][0][1])

	yMean = sum(y) / len(y)

	for i in xrange(len(box)):

		if (box[i][0][1] < yMean):
			top.append(box[i][0])

	topLeft = ()
	topRight = ()

	if top[0][0] < top[1][0]:
		topLeft = top[0]
		topRight = top[1]
	else:
		topLeft = top[1]
		topRight = top[0]


	return topRight[0] - topLeft[0]

def getCoordPointsFromBox(box):

  y = []

  top = []

  for i in xrange(len(box)):
    #print box[i]
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

  #print (topLeft[0], topLeft[1], topRight[0] - topLeft[0])


  return (topLeft[0], topLeft[1], topRight[0] - topLeft[0])

# Get the distance given 
def distance_to_camera(knownDistance, knownWidthPx, width):
	# compute and return the distance from the maker to the camera
	return (knownWidthPx / width) * knownDistance


def featureDetector(img1, img2, img2Clr, times):
	# img1 = cv2.imread(templateFileName, 0)          # queryImage
	# img2Clr = cv2.imread(trainFileName) # trainImage
	# img2Clr = cv2.resize(img2Clr, (0,0), fx = 0.125, fy = 0.125, interpolation = cv2.INTER_AREA);
	# img2 = cv2.cvtColor(img2Clr, cv2.COLOR_RGB2GRAY)

	i = 0
	#while(i < times):

	sift = cv2.xfeatures2d.SIFT_create()

	# find the keypoints and descriptors with SIFT
	kp1, des1 = sift.detectAndCompute(img1,None)
	kp2, des2 = sift.detectAndCompute(img2,None)

	# FLANN parameters
	FLANN_INDEX_KDTREE = 0
	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks=50)   # or pass empty dictionary

	flann = cv2.FlannBasedMatcher(index_params,search_params)

	matches = flann.knnMatch(des1,des2,k=2)

	# store all the good matches as per Lowe's ratio test.
	good = []
	for m,n in matches:
	    if m.distance < 0.7*n.distance:
	        good.append(m)

	dst = 0

	print len(good)

	if len(good) > MIN_MATCH_COUNT:
	    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

	    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
	    matchesMask = mask.ravel().tolist()

	    h,w = img1.shape
	    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	    dst = cv2.perspectiveTransform(pts,M)

	    img2Clr = cv2.polylines(img2Clr,[np.int32(dst)], True, (255, 255, 0), 3, cv2.LINE_AA)

	    #plt.imshow(img2Clr, 'gray'),plt.show()
	    cv2.imwrite('res1-box.png', img2Clr)

	else:
	    print "Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT)
	    matchesMask = None

	    return []

	draw_params = dict(matchColor = (0,255,0), # draw matches in green color
	                   singlePointColor = None,
	                   matchesMask = matchesMask, # draw only inliers
	                   flags = 2)

	img3 = cv2.drawMatches(img1,kp1,img2Clr,kp2,good,None,**draw_params)
	cv2.imwrite('res1-matches.png', img3)

	return dst

def getFeatures(templateFileName, trainFileName, knownWidthPx, knownDistance):
	img1 = cv2.imread(templateFileName, 0)          # queryImage
	img2Clr = cv2.imread(trainFileName) # trainImage
	img2Clr = cv2.resize(img2Clr, (0,0), fx = 1.0, fy = 1.0, interpolation = cv2.INTER_AREA);
	img2 = cv2.cvtColor(img2Clr, cv2.COLOR_RGB2GRAY)

	#boxCoordinates = featureDetector(templateFileName, trainFileName, 1)
	boxCoordinates = featureDetector(img1, img2, img2Clr, 1)

	print boxCoordinates

	#if boxCoordinates == []:
	#	return (-1, -1)

	returnBoxCoordinates = []
	distances = []

	while boxCoordinates != []:

		widthPx = sortPoints(boxCoordinates)

		inches = distance_to_camera(knownDistance, knownWidthPx*1.0, widthPx*1.0)

		(img2, smoothBoxCoordinates) = removePoints(img2, boxCoordinates)
		cv2.imwrite('res1-matchesAfter.png', img2)

		returnBoxCoordinates.append(smoothBoxCoordinates)
		distances.append(inches)

		boxCoordinates = featureDetector(img1, img2, img2Clr, 1)

	return (returnBoxCoordinates, distances)


def calibrateImage(templateFileName, trainFileName):

	img1 = cv2.imread(templateFileName, 0)          # queryImage
	img2Clr = cv2.imread(trainFileName) # trainImage
	img2Clr = cv2.resize(img2Clr, (0,0), fx = 1.0, fy = 1.0, interpolation = cv2.INTER_AREA);
	img2 = cv2.cvtColor(img2Clr, cv2.COLOR_RGB2GRAY)

	boxCoordinates = featureDetector(img1, img2, img2Clr, 1)

	if boxCoordinates == []:
		return []
	
	widthPx = sortPoints(boxCoordinates)

	return widthPx

'''
1. Experimentally determine ratio of x-displacement to depth (R)
(ie for specific depth d, and world coord x-displacement to reach edge of screen x
R = x / d)
2. For new depth D, the edge of the screen is X units away where X = D * R
3. Assuming linear relationship between world coord and screen space
the x-displacement of the centroid is X * (centroid_x_im / im_width)
'''
def getXcoord(depth, bbox):
	cx = 480 # center of the screen
	print(bbox[0], bbox[2], cx)
	xPix = bbox[0] + bbox[2] - cx
	xDepthRatio = 13.7 / 34 # Experimental ratio of x displacement to depth (world coord)
	return (depth, xDepthRatio * depth * (xPix / float(cx))) #returns tuple of x-displacement and y-disp (depth)
  


#knownWidthPx = calibrateImage('Honey_Nut_Cheerios.png', 'im0.png')
# knownWidthPx = 169.114
# knownDistance = 24
# print knownWidthPx

#print knownWidthPx
# (boxCoordinates, distance) = getFeatures('Honey_Nut_Cheerios.png', 'im72.png', knownWidthPx, knownDistance)
# print distance
# print boxCoordinates



