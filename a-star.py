from pyamaze import maze, agent, COLOR, textLabel
from queue import PriorityQueue
 
def h(cell1, cell2):
    x1, y1 = cell1
    x2, y2 = cell2
    return abs(x1 - x2) + abs(y1 - y2)

def aStar(m):
    start = (m.rows, m.cols)
    goal = (1, 1)
    open = PriorityQueue()
    open.put((0, start))
    came_from = {}
    g_score = {cell: float('inf') for cell in m.maze_map}
    g_score[start] = 0
    f_score = {cell: float('inf') for cell in m.maze_map}
    f_score[start] = h(start, goal)

    while not open.empty():
        current = open.get()[1]

        if current == goal:
            break

        for d in 'ESNW':
            if m.maze_map[current][d]:
                if d == 'E':
                    neighbor = (current[0], current[1] + 1)
                elif d == 'W':
                    neighbor = (current[0], current[1] - 1)
                elif d == 'S':
                    neighbor = (current[0] + 1, current[1])
                elif d == 'N':
                    neighbor = (current[0] - 1, current[1])

                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + h(neighbor, goal)
                    if neighbor not in [i[1] for i in open.queue]:
                        open.put((f_score[neighbor], neighbor))

    path = {}
    cell = goal
    while cell != start:
        path[came_from[cell]] = cell
        cell = came_from[cell]
    return path

if __name__ == '__main__':
    m = maze(20, 20)
    m.CreateMaze(loopPercent=100)
    path = aStar(m)

    a = agent(m, footprints=True, color=COLOR.green, filled=True)

    m.tracePath({a: path}, delay=300) 
    l = textLabel(m, 'A* Path Length', len(path) + 1) 
    m.run()
