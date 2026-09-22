from pyamaze import maze, agent, COLOR ,textLabel
from collections import deque

def BFS(m):
    start = (m.rows, m.cols)
    explored = [start]
    frontier = [start]
    bfsPath={}
    while len(frontier) > 0:
        currCell = frontier[0]
        if currCell == (1, 1):
            break
        frontier.remove(currCell)
        for d in 'ESNW':
            if m.maze_map[currCell][d] == True:
                if d == 'E':
                    childCell = (currCell[0], currCell[1] + 1)
                if d == 'W':
                    childCell = (currCell[0], currCell[1] - 1)
                if d == 'S':
                    childCell = (currCell[0] + 1, currCell[1])
                if d == 'N':
                    childCell = (currCell[0] - 1, currCell[1])
                if childCell in explored:
                    continue
                explored.append(childCell)
                frontier.append(childCell)
                bfsPath[childCell] = currCell
    fwdPath = {}
    cell = (1, 1)
    while cell != start:
        fwdPath[bfsPath[cell]] = cell
        cell = bfsPath[cell]
    return fwdPath

if __name__ == '__main__':
    m = maze(10, 10)
    m.CreateMaze(loopPercent=100)
    path = BFS(m)

    a = agent(m, footprints=True, color=COLOR.red, filled=True)

    m.tracePath({a:path}, delay=300) 
    l=textLabel(m, 'BFS Path Length', len(path) + 1) 
    m.run()