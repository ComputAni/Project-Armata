from math import sqrt
from itertools import product

class AStar(object):
    def __init__(self, graph):
        self.graph = graph

    #Astar search algorithm
    def search(self, start, end):
        openset = set()
        closedset = set()
        current = start
        openset.add(current)

        while openset:
            #Will change this to be a minheap later, but right now just finds the min heuristic cost
            #from the set using a lambda
            current = min(openset, key=lambda o:o.g + o.h)

            #If we reached our goal, add to result list
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]

            #Otherwise, remove from nodes to visit, and add to closed
            openset.remove(current)
            closedset.add(current)

            #Iterate over all neighbors
            for node in self.graph[current]:
                if node in closedset:
                    continue
                #If node can be explored, calculate its new cost, update cost only if its less
                if node in openset:
                    new_g = current.g + current.move_cost(node)
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                #Otherwise, calculate heuristic, manhattan distance, and update "path" by setting parent
                #Also add to openset to be considered on the frontier
                else:
                    node.g = current.g + current.move_cost(node)
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None


class AStarNode(object):
    def __init__(self):
        self.g = 0
        self.h = 0
        self.parent = None

#Heuristic is manhattan distance rn
class AStarGrid(AStar):
    def heuristic(self, node, start, end):
        return sqrt((end.x - node.x)**2 + (end.y - node.y)**2)


class AStarGridNode(AStarNode):
    def __init__(self, x, y):
        self.x, self.y = x, y
        super(AStarGridNode, self).__init__()

    #Using arbitrary values i found online, will need to figure out later
    def move_cost(self, other):
        diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
        return 14 if diagonal else 10

#Graph is basically (AStarGridNode,obstacle='y','n')
def make_graph(width, height):
    nodes = [[((AStarGridNode(x, y)), 0) for y in range(height)] for x in range(width)]
    graph = {}
    for x, y in product(range(width), range(height)):
        node = nodes[x][y][0]
        graph[node] = []
        #I wrote it this way to allow for easy expanding to 8 directional movement (diagonals), rn its N,S,W,E
        for i, j in product([-1, 0, 1], [-1, 0, 1]):
            if not (0 <= x + i < width):
                continue
            if not (0 <= y + j < height):
                continue
            if (abs(i) == abs(j)):
                continue
            graph[nodes[x][y][0]].append(nodes[x+i][y+j][0])
    return graph, nodes



g,n = make_graph(9,9)
paths = AStarGrid(g)
start = n[0][0][0]
end = n[7][8][0]

shortestPath = paths.search(start,end)

res = []
for node in shortestPath:
    res.append((node.x,node.y))

print res