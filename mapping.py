from math import sqrt
from itertools import product
from Queue import PriorityQueue
import copy
import random
import sys
import argparse


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
    return

def move_backward():
    return

def rotate_cw():
    return

def rotate_ccw():
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
            print "reversed"
            move_backward()
            newOrientation = orientation
            return (newOrientation, turned)
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
            print "reversed"
            move_backward()
            newOrientation = orientation
            return (newOrientation, turned)
        elif (orientation == "E"):
            move_forward()
        else:
            move_forward()
        newOrientation = "E"
    #Going south
    elif (delta == (-1,0)):
        if (orientation == "N"):
            print "reversed"
            move_backward()
            newOrientation = orientation
            return (newOrientation, turned)
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
            print "reverse"
            move_backward()
            newOrientation = orientation
            return (newOrientation, turned)
        else:
            move_forward()
        newOrientation = "W"

    return (newOrientation, turned)

#CV Routine
def obstacles():
    return


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

#Main loop, basically just infinite loops until we reach ending path
#It gets the route, extracts the next move, motion plans said move
#Updates obstacles if necessary, and repeats until reach goal
def main(start, end):
    numRows = 9
    numCols = 4
    g = make_graph(numRows, numCols)
    n = neighbors(g, numRows, numCols)

    start_x, start_y = start
    end_x, end_y = end

    start = g[start_x][start_y]
    end = g[end_x][end_y]
#    start = g[0][2]
#    end = g[4][2]

    curr = start
    res = []
    i= 0

    currentOrientation = "N"


    #print_neighbors(n,numRows,numCols)
    #print_graph(g, numRows, numCols)


    print "Starting at: ", print_node(curr)
    print "Ending at: ", print_node(end)
    print "with orientation: ", currentOrientation

    while (curr != end):

        #Detect obstacles
        #g,n = obstacles(g,n, obstacle_weight, numRows, numCols, curr.row, curr.col, knownDistance, knownWidthPx)

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

        if ((curr.row == 0) and (curr.col == 3)):
            g,n = update_weight(4,3,g,n, 1000, numRows, numCols)

        if ((curr.row == 0) and (curr.col == 2)):
            g,n = update_weight(3,2,g,n, 1000, numRows, numCols)
            g,n = update_weight(3,1,g,n, 1000, numRows, numCols)

        if ((curr.row == 3) and (curr.col == 3)):
            g,n = update_weight(4,3,g,n, 1000, numRows, numCols)

        #print_graph(g, numRows, numCols)





    res.append(end)
    print_res = []
    for node in res:
        print_res.append((node.row,node.col))

    print print_res


parser = argparse.ArgumentParser(description = 'Process display arguments')
parser.add_argument('-s', nargs = '?', default = '1,1')
parser.add_argument('-e', nargs = '?', default = '2,2')
args = parser.parse_args()

START_LIST = args.s.split(",")
END_LIST = args.e.split(",")

START = (int(START_LIST[0]), int(START_LIST[1]))
END = (int(END_LIST[0]), int(END_LIST[1]))

print END

main(START, END)