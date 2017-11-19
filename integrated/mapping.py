from math import sqrt
import sys
from itertools import product
from Queue import PriorityQueue
import copy
import random
import threadDrive
import RPi.GPIO as gpio
from featureDetection import *
from test_image import takeIm
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


#Orientations for the robot, facing N (default)
orientations = ["N", "S", "W", "E"]


class Node(object):
    def __init__(self, r,c, state, weight):
        self.row = r
        self.col = c
        self.state = state
        self.weight = weight



#Generates a graph which is just a list of (x,y) nodes
def make_graph(numRows, numCols):
    res = []

    for i in xrange(numRows):
        tr = []
        for j in xrange(numCols):
            weight = 1 #+ random.randint(0,1)
            tr.append(Node(i,j,"empty", weight))
        res.append(tr)

    return res


#Just makes sure we're inside the grid
def inBounds(row,col, numRows, numCols):
    return row >= 0 and col >= 0 and row < numRows and col < numCols

#Given a node (x,y), finds the neighbors of this node. For our purposes, only 4 
#such neighbors, up down left right (no diagnals for now)
def neighbors(graph, numRows, numCols):
    neighbors = dict()
    
    dirs = [(0,1), (0,-1), (1,0), (-1,0)]
    for row in graph:
        for node in row:
            neighbors[node] = set()
            for (x,y) in dirs:
                cr,cc = node.row + x, node.col + y
                if inBounds(cr,cc,numRows, numCols):
                    neighbors[node].add(graph[cr][cc])

    return neighbors

#Heuristic function for manhatten distance
def heuristic(node1, node2):

    (x1,y1) = node1.row, node1.col
    (x2,y2) = node2.row, node2.col

    return abs(x1-x2) + abs(y1-y2)


def cost(node1, node2):
    #Just return the cost of going to this node (we can make this more advanced later)
    return node2.weight

#Astar search algorithm, keeps iterating until no more nodes to explore/reached the end
def astar_search(graph, neighbors, start, end):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while (not frontier.empty()):
        current = frontier.get()

        if (current == end):
            break

        for n in neighbors[current]:
            new_cost = cost_so_far[current] + cost(current, n)

            if ((new_cost < 1000) and ((n not in cost_so_far) or (new_cost < cost_so_far[n]))):
                cost_so_far[n] = new_cost
                priority = new_cost + heuristic(end, n)
                frontier.put(n, priority)
                came_from[n] = current

    return came_from


#Given the path returned by astar, just adds to a list to make it a nice readable path
def generate_path(path, end):
    res = []
    res.append(end)

    curr = path[end]

    while (curr != None):
        res.append(curr)
        curr = path[curr]

    res.pop()
    return res

def update_weight(r,c,g,n,w, numRows, numCols):

    #Update entry in graph
    node = g[r][c]
    neighbors = copy.copy(n[node])

    del n[node]

    node.weight = w
    n[node] = neighbors

    return g,n


def move_forward():
    global motorL
    threadDrive.forward(motorL, FORWARD_TICKS)
    print("Moved Forward")
    return

def move_backward():
    threadDrive.forward(motorL, BACKWARD_TICKS)
    print("Moved Backward")
    return

def rotate_cw():
    global motorL
    threadDrive.cw(motorL, CW_TICKS)
    print("Turned clockwise")
    return

def rotate_ccw():
    global motorL
    threadDrive.cw(motorL, CCW_TICKS)
    print("Turned counter clockwise")
    return

#Given the current and new locations, and the orientation, returns some motor_api
#call that instructs the robot to move accordingly, at the end will update the orientation
def motion_plan(curr, new, orientation):
    currX,currY = curr.row, curr.col
    newX,newY = new.row, new.col

    deltaX = newX - currX
    deltaY = newY - currY

    delta = (deltaX,deltaY)

    turned = False

    # print delta

    #Going north
    if (delta == (1,0)):
        if (orientation == "N"):
            #Go straight, since we're already facing this direction
            move_forward()
        elif (orientation == "S"):
            move_backward()
        elif (orientation == "W"):
            rotate_cw()
            #move_forward()
            turned = True
        elif (orientation == "E"):
            rotate_ccw()
            #move_forward()
            turned = True
        else:
            move_forward()
        newOrientation = "N"
    #Going east
    elif (delta == (0,1)):
        if (orientation == "N"):
            rotate_cw()
            #move_forward()
            turned = True
        elif (orientation == "S"):
            rotate_ccw()
            #move_forward()
            turned = True
        elif (orientation == "W"):
            move_backward()
        elif (orientation == "E"):
            move_forward()
        else:
            move_forward()
        newOrientation = "E"
    #Going south
    elif (delta == (-1,0)):
        if (orientation == "N"):
            move_backward()
        elif (orientation == "S"):
            move_forward()
        elif (orientation == "W"):
            rotate_ccw()
            # move_forward()
            turned = True
        elif (orientation == "E"):
            rotate_cw()
            #move_forward()
            turned = True
        else:
            #Default to just go forward
            move_forward()

        #Update orientation to face the direction of movement
        newOrientation = "S"
    #Going west
    elif (delta == (0,-1)):
        if (orientation == "N"):
            rotate_ccw()
            #move_forward()
            turned = True
        elif (orientation == "S"):
            rotate_cw()
            #move_forward()
            turned = True
        elif (orientation == "W"):
            move_forward()
        elif (orientation == "E"):
            move_backward()
        else:
            move_forward()
        newOrientation = "W"

    return (newOrientation, turned)


#Tuple of (x,y), normalizes to grid
def box_round(coords):
    (x,y) = coords

    isNegX = -1 if (x < 0.0) else 1
    isNegY = -1 if (y < 0.0) else 1

    new_x = (int(abs(x)) + (GRID_SIZE / 2)) / GRID_SIZE
    new_y = (int(abs(y)) + (GRID_SIZE / 2)) / GRID_SIZE

    new_x = isNegX * new_x
    new_y = isNegY * new_y

    return (new_x, new_y)


#CV Routine
def obstacles(g,n, obstacle_weight, numRows, numCols, curr_X, curr_Y, knownDistance, knownWidthPx):
    global GRID_SIZE, IMAGE_COUNT

    file_name = "im" + str(IMAGE_COUNT) + ".png"
    takeIm(file_name)
    IMAGE_COUNT += 1

    (boxCoordinates, distances) = getFeatures('Honey_Nut_Cheerios.png', file_name, knownWidthPx, knownDistance)

    print "Distance after feature detection: ", distances

    obstacle_list = []
    # for (i,coord) in enumerate(boxCoordinates):
    #     points = getCoordPointsFromBox(coord)
    #     obstacle_list.append(getXcoord(distances[i], points))
    print "boxCoordinates: ", boxCoordinates, len(boxCoordinates) 
    for i in xrange(len(boxCoordinates)):
        #print boxCoordinates[i]
        points = getCoordPointsFromBox(boxCoordinates[i])
        print points
        obstacle_list.append(getXcoord(distances[i], points)) 

    print "obstacle_list", obstacle_list

    for (i,(x,y)) in enumerate(obstacle_list):
        #convert
        obstacle_list[i] = box_round((x,y))

    print "Detected %d obstacles" % len(obstacle_list)
    print "Detected obstacles: ", obstacle_list

    for (x,y) in obstacle_list:
        obstacle_X, obstacle_Y = (curr_X + x, curr_Y + y)

        print "Actual obstacle location: ", (obstacle_X, obstacle_Y)

        if ((obstacle_X != curr_X) or (obstacle_Y != curr_Y)):
            print "Updating weight"
            g,n = update_weight(obstacle_X, obstacle_Y,g,n, obstacle_weight, numRows, numCols)
    
    return g,n

def print_graph(g, numRows, numCols):
    for i in range(numRows):
        for j in range(numCols):
            node = g[i][j]

            print (node.row, node.col, node.weight)

def print_neighbors(n, numRows, numCols):

    for node in n:
        neighbs = n[node]
        print node.row,node.col

        for nNode in neighbs:
            print "foo: ", nNode.row, nNode.col, nNode.weight

def print_node(n):
    print (n.row, n.col, n.weight)
    return

def print_result(res):
    print_res = []
    for node in res:
        print_res.append((node.row,node.col))

    print print_res

#Main loop, basically just infinite loops until we reach ending path
#It gets the route, extracts the next move, motion plans said move
#Updates obstacles if necessary, and repeats until reach goal
def main(numRows, numCols,start, end):
    g = make_graph(numRows, numCols)
    n = neighbors(g, numRows, numCols)
    start_x, start_y = start
    end_x, end_y = end

    start = g[start_x][start_y]
    end = g[end_x][end_y]

    curr = start
    res = []
    i = 0
    
    obstacle_weight = 1000
    currentOrientation = "N"

    #update_weight(3,2,g,n, 1000, numRows, numCols)

    print "Starting at: ", print_node(curr)
    print "with orientation: ", currentOrientation

    while (curr != end):

        #Detect obstacles
        g,n = obstacles(g,n, obstacle_weight, numRows, numCols, curr.row, curr.col, knownDistance, knownWidthPx)

        #Plan new route, assuming new information given
        p = astar_search(g, n, curr,end)
        path = generate_path(p, end)

        #The next node to take is at the end of the list
        new = path[-1]

        #Use robot API to maneuver, given current orientation and nodes to go to
        (newOrientation, turned) = motion_plan(curr, new, currentOrientation)
        #print newOrientation
        
        #Update states, if we don't turn, add current node to result list
        #Update current to be newly planned node
        if (not(turned)):
            res.append(curr)
            curr = new
        else:
            print "Turned!"

        currentOrientation = newOrientation

        print "After algorithms, current: " , curr.row, curr.col, currentOrientation, end.row, end.col

        #print_graph(g, numRows, numCols)


    res.append(end)
    print_result(res)



def cleanup():
    #global CAMERA

    #CAMERA.close()
    gpio.cleanup()

######GLOBALS AND CONSTANTS INITIALIZATIONS
#Initialize motors
gpio.setmode(gpio.BOARD)
a = threadDrive.motor(18, 22, 12, 16)
b = threadDrive.motor(38, 40, 32, 36)
c = threadDrive.motor(31, 33, 35, 37)
d = threadDrive.motor(3, 5, 7, 11)
motorL = [a, b, c, d]
CW_TICKS = 2150
CCW_TICKS = -2200
FORWARD_TICKS = 5600
BACKWARD_TICKS = -5600


#Calibrate camera subsystem
knownWidthPx = calibrateImage('Honey_Nut_Cheerios.png', 'calibrate.png')
#knownWidthPx = 180.99
print knownWidthPx
knownDistance = 24


#Globals for the obstacle course
NUM_OBSTACLES = 2
GRID_SIZE = 24
NUM_ROWS = 9
NUM_COLS = 4
START_X = int(sys.argv[1])
START_Y = int(sys.argv[2])
END_X = int(sys.argv[3])
END_Y = int(sys.argv[4])

START = (START_X, START_Y)
END = (END_X, END_Y)

#Camera initialization
cap = cv2.VideoCapture() # Video capture object
cap.open(0) # Enable the camera
IMAGE_COUNT = 1


main(NUM_ROWS, NUM_COLS, START, END)
cleanup()
