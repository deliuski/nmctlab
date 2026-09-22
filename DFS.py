from pyamaze import maze , agent , COLOR ,textLabel


def DFS(m):
    start = (m.rows, m.cols)
    explored = [start]
    frontier = [start]
    dfsPath={}
    while len(frontier) > 0:
        currCell = frontier[-1]
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
                dfsPath[childCell] = currCell
    fwdPath = {}
    cell = (1, 1)
    while cell != start:
        fwdPath[dfsPath[cell]] = cell
        cell = dfsPath[cell]
    return fwdPath
                
if __name__ == '__main__':
    m = maze(20, 20)
    m.CreateMaze(loopPercent=100)
    path = DFS(m)

    a = agent(m, footprints=True, color=COLOR.blue, filled=True)

    m.tracePath({a:path}, delay=300) 
    l=textLabel(m, 'DFS Path Length', len(path) + 1) 
    m.run()
