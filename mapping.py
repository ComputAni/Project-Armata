from math import sqrt
from itertools import product
from Queue import PriorityQueue
import random

#Orientations for the robot, facing N (default)
orientations = ["N", "S", "W", "E"]


#Generates a graph which is just a list of (x,y) nodes
def make_graph(numRows, numCols):
    res = []

    for i in xrange(numRows):
        for j in xrange(numCols):
            weight = 1 #+ random.randint(0,1)
            res.append((i,j,"empty", weight))
    return res


#Just makes sure we're inside the grid
def inBounds(row,col, numRows, numCols):
    return row >= 0 and col >= 0 and row < numRows and col < numCols

#Given a node (x,y), finds the neighbors of this node. For our purposes, only 4 
#such neighbors, up down left right (no diagnals for now)
def neighbors(graph, numRows, numCols):
    neighbors = dict()
    
    dirs = [(0,1), (0,-1), (1,0), (-1,0)]
    for node in graph:
        neighbors[node] = set()
        for (x,y) in dirs:
            cr,cc = node[0] + x, node[1] + y
            if inBounds(cr,cc,numRows, numCols):
                neighbors[node].add(graph[numCols*cr + cc])

    return neighbors

#Heuristic function for manhatten distance
def heuristic(node1, node2):

    (x1,y1) = node1[0], node1[1]
    (x2,y2) = node2[0], node2[1]

    return abs(x1-x2) + abs(y1-y2)


def cost(node1, node2):
    #Just return the cost of going to this node (we can make this more advanced later)
    return node2[3]

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

#Basically does two things, first updates the Node weight in our graph representation (list)
#Then also updates the neighbors "understanding" of the current node (e.g updates the weights in the neighbor lists)
#I can definitely make this better, will try soon
def updateWeight(index, node, g,n, w, numRows, numCols):
    original = node
    temp = list(g[index])
    temp[3] = w
    new = tuple(temp)
    g[index] = new

    newNode = g[index]
    n[newNode] = n.pop(node)

    dirs = [(0,1), (0,-1), (1,0), (-1,0)]
    for (x,y) in dirs:
        cr,cc = newNode[0] + x, newNode[1] + y
        if (inBounds(cr,cc, numRows, numCols)):
            nIndex = numRows*cr + cc
            neighborNode = g[nIndex]

            neighbors = n[neighborNode]
            if (original in neighbors):
                neighbors.remove(original)
                neighbors.add(newNode)
                n[neighborNode] = neighbors

    return g,n


#Given the current and new locations, and the orientation, returns some motor_api
#call that instructs the robot to move accordingly, at the end will update the orientation
def motion_plan(curr, new, orientation):
    return "N"
    



#Main loop, basically just infinite loops until we reach ending path
#It gets the route, extracts the next move, motion plans said move
#Updates obstacles if necessary, and repeats until reach goal
def main():
    numRows = 9
    numCols = 9
    g = make_graph(numRows, numCols)
    n = neighbors(g, numRows, numCols)
    start = g[0]
    end = g[70]

    curr = start
    count = 1

    res = []
    i= 0

    currentOrientation = "N"

    while (curr != end):
        
        #Plan new route, assuming new information given
        p = astar_search(g, n, curr,end)
        path = generate_path(p, end)

        #Add the next node we're taking to the result, the next node to take is at the end of the list
        res.append(curr)
        new = path[-1]

        #Use robot API to maneuver, given current orientation and nodes to go to
        newOrientation = motion_plan(curr, new, currentOrientation)
        
        #Update states
        curr = new
        currentOrientation = newOrientation


        if (i == 1):
            g,n = updateWeight(4, g[4], g , n, 1000, numRows, numCols)
            pass
        elif (i == 4):
            g,n = updateWeight(60, g[60], g , n, 1000, numRows, numCols)
            g,n = updateWeight(61, g[61], g , n, 1000, numRows, numCols)
            pass
        elif (i == 7):
            g,n = updateWeight(69, g[69], g , n, 1000, numRows, numCols)
            pass
        i +=1

    res.append(end)

    #print g[60]

    print res


main()