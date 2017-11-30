import math, sys, copy, random, time, cv2
from itertools import product
from Queue import PriorityQueue
import threadDrive
import RPi.GPIO as gpio
from featureDetection import *
from test_image import takeIm
from picamera.array import PiRGBArray
from picamera import PiCamera
from simpleServer import *
from cleanup import cleanUpRun

############################################
"""
This is the main script of our 18-500 ECE Capstone project. We are Project Armada
Group 4a. Our project is an autonomous search and explore robot that uses computer vision
and motion planning to get to the desired end point. We have two interfaces: cmd line and iOS app.
To use command line, simply run "python mapping.py start_row start_col end_row end_col" where each of the 
4 following arguments are valid integers within the course (9x4). If you want to use the iOS app, simply
run "python mapping.py" and interface the program with the app (this interface is explained on the iOS app itself).

The current dimensions of the course are a 9 row by 4 column grid, but all code and logic scales 
to these global variables. To change the size of the course, check out NUM_ROWS, NUM_COLS in our global variable
section.
"""
############################################


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
def inBounds(row,col, num_rows, num_cols):
    return row >= 0 and col >= 0 and row < num_rows and col < num_cols

#Boundaries are:
#North, South, West, East, NW, NE, SW,SE
#Returns the orientations of the robot that satisfy the condition of facing outwards
#Return None if the robot is in an interior point
def get_boundary(row,col, num_rows, num_cols):
    
    if (not(inBounds(row, col, num_rows, num_cols))):
        return None

    if (row == 0):
        if (col == 0):
            return "SW"
        elif (col == (num_cols) - 1):
            return "SE"
        else:
            return "S"
    elif (row == (num_rows-1)):
        if (col == 0):
            return "NW"
        elif (col == (num_cols) - 1):
            return "NE"
        else:
            return "N"
    elif (col == 0):
        return "W"
    elif (col == (num_cols-1)):
        return "E"
    else:
        return None


#Given the current node and the orientation, determine if node is on the boundary
#If so, return if orientation of robot is facing outside of the boundary
#If this is the case, then we do not need to detect obstacles
def valid_position(curr_node, curr_orientation, num_rows, num_cols):
    curr_row,curr_col = curr_node.row, curr_node.col

    orientations = get_boundary(curr_row, curr_col, num_rows, num_cols)

    if (orientations != None):
        return not(curr_orientation in orientations)

    return True


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

    #Going north
    if (delta == (1,0)):
        if (orientation == "N"):
            #Go straight, since we're already facing this direction
            move_forward()
        elif (orientation == "S"):
            move_backward()
            new_orientation = orientation
            return (new_orientation, turned)
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
        new_orientation = "N"
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
            new_orientation = orientation
            return (new_orientation, turned)
        elif (orientation == "E"):
            move_forward()
        else:
            move_forward()
        new_orientation = "E"
    #Going south
    elif (delta == (-1,0)):
        if (orientation == "N"):
            move_backward()
            new_orientation = orientation
            return (new_orientation, turned)
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
        new_orientation = "S"
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
            new_orientation = orientation
            return (new_orientation, turned)
        else:
            move_forward()
        new_orientation = "W"

    return (new_orientation, turned)


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
def obstacles(g,n, obstacle_weight, numRows, numCols, curr_X, curr_Y, knownDistance, knownWidthPx, end_point):
    global GRID_SIZE, IMAGE_COUNT, SCREENW

    file_name = "im" + str(IMAGE_COUNT) + ".png"
    takeIm(file_name)
    IMAGE_COUNT += 1
    startTime = time.time()
    (boxCoordinates, distances) = getFeatures('Honey_Nut_Cheerios.png', file_name, knownWidthPx, knownDistance)
    finishTime = time.time()
    print("Feature time: " + str(finishTime - startTime))
    print "Distance after feature detection: ", distances

    obstacle_list = []

    print "boxCoordinates: ", boxCoordinates, len(boxCoordinates) 
    for i in xrange(len(boxCoordinates)):
        points = getCoordPointsFromBox(boxCoordinates[i])
        print points
        obstacle_list.append(getXcoord(distances[i], points, SCREENW/2)) 

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
            if ((obstacle_X == end_point[0]) and (obstacle_Y == end_point[1])):
                print "Obstacle detected at the end location! Aborting mission."
                return None, None

            if (inBounds(obstacle_X, obstacle_Y, numRows, numCols)):
                print "Updating weight"
                g,n = update_weight(obstacle_X, obstacle_Y,g,n, obstacle_weight, numRows, numCols)
            else:
                print "Out of bounds obstacle detected at: ", obstacle_X, obstacle_Y
    
    return g,n

def print_graph(g, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            node = g[i][j]

            print (node.row, node.col, node.weight)

def print_neighbors(n, num_rows, num_cols):

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
def main(numRows, numCols,main_start, main_end):

    print "Starting main mapping routine!"

    #Initialize graph, initialize neighbors
    g = make_graph(numRows, numCols)
    n = neighbors(g, numRows, numCols)
    start_x, start_y = main_start
    end_x, end_y = main_end
    end_point = main_end
    map_start = g[start_x][start_y]
    map_end = g[end_x][end_y]

    #Current node we're at
    curr = map_start
    #Result list of nodes robot took to reach final destination
    res = []
    #Initialize weight of obstacles to be 1000 (arbitrary, for A* search)
    obstacle_weight = 1000
    #Initialize current orientation to be North, with localization, we can change this,
    #But currently, just manually place robot in this orientation
    current_orientation = "N"

    print "Starting at: ", print_node(curr)
    print "with orientation: ", current_orientation

    while (curr != map_end):

        #Detect obstacles
        if (valid_position(curr, current_orientation, numRows, numCols)):
            g,n = obstacles(g,n, obstacle_weight, numRows, numCols, curr.row, curr.col, knownDistance, knownWidthPx, end_point)

        #If invalid obstacle detected (aka at end point), abort mission
        if ((g == None) and (n == None)):
            print "Aborting mission, no path!"
            return None

        #Plan new route, assuming new information given
        p = astar_search(g, n, curr, map_end)
        path = generate_path(p, map_end)
        #The next node to take is at the end of the list
        new = path[-1]

        #Use robot API to maneuver, given current orientation and nodes to go to
        (new_orientation, turned) = motion_plan(curr, new, current_orientation)
        
        #Update states, if we don't turn, add current node to result list
        #Update current to be newly planned node
        if (not(turned)):
            res.append(curr)
            curr = new
        else:
            print "Turned!"

        current_orientation = new_orientation

        print "After algorithms, current: %d,%d, Orientation: %s" % (curr.row, curr.col, current_orientation)
        #print_graph(g, numRows, numCols)


    res.append(map_end)
    print_result(res)



def cleanup_seq():
    #global CAMERA

    #CAMERA.close()
    gpio.cleanup()

######GLOBALS AND CONSTANTS INITIALIZATIONS
#Cleanup previous state, Initialize motors
cleanUpRun()
print "Cleaned up"
gpio.setmode(gpio.BOARD)
a = threadDrive.motor(18, 22, 12, 16, 0)
b = threadDrive.motor(38, 40, 32, 36, 0)
c = threadDrive.motor(31, 33, 35, 37, 0)
d = threadDrive.motor(3, 5, 7, 11, 0)
motorL = [a, b, c, d]
threadDrive.forward(motorL, 0)

CW_TICKS = 2150
CCW_TICKS = -2200
FORWARD_TICKS = 5600
BACKWARD_TICKS = -5600
SCREENW = 960


#Calibrate camera subsystem
#knownWidthPx = calibrateImage('Honey_Nut_Cheerios.png', 'calibrate.png')
knownWidthPx = 254.59

print "KnownWidthPx", knownWidthPx
knownDistance = 24


#Globals for the obstacle course
#GRID_SIZE in inches (e.g 2 tiles)
NUM_OBSTACLES = 2
GRID_SIZE = 24
#Using a 9x4 grid
NUM_ROWS = 9
NUM_COLS = 4

#If command line args detected, use them as start, end
#Otherwise use start,end from mobile app
if (len(sys.argv) > 1):
    print "Found command line args"
    START_X = int(sys.argv[1])
    START_Y = int(sys.argv[2])
    END_X = int(sys.argv[3])
    END_Y = int(sys.argv[4])

    START = (START_X, START_Y)
    END = (END_X, END_Y)
else:
    "Using iOS args"
    START,END = server_run()

#Check if start and end positions are valid
if (not(inBounds(START[0],START[1], NUM_ROWS, NUM_COLS))):
    print "Invalid start coordinate given! Aborting mission!"
if (not(inBounds(END[0],END[1], NUM_ROWS, NUM_COLS))):
    print "Invalid end coordinate given! Aborting mission!"

#Camera initialization
cap = cv2.VideoCapture() # Video capture object
cap.open(0) # Enable the camera
IMAGE_COUNT = 1

##RUNNING MAIN LOOP, initialize server to get coordinates, then run main
main(NUM_ROWS, NUM_COLS, START, END)
cleanup_seq()
