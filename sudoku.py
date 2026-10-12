import copy
import time


def neighbors(row, col):
    """All cells that share a constraint with (row, col)."""
    result = set()
    for x in range(9):
        result.add((row, x))
        result.add((x, col))
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            result.add((start_row + i, start_col + j))
    result.discard((row, col))
    return result


NEIGHBORS = {(r, c): neighbors(r, c) for r in range(9) for c in range(9)}


def is_valid_move(grid, row, col, num):
    for (r, c) in NEIGHBORS[(row, col)]:
        if grid[r][c] == num:
            return False
    return True


def empty_cells(grid):
    return [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]


def legal_values(grid, row, col):
    """Current domain of an empty cell."""
    return [n for n in range(1, 10) if is_valid_move(grid, row, col, n)]


# ---------------- Variable ordering ----------------

def select_first(grid):
    """No heuristic: first empty cell (row by row)."""
    cells = empty_cells(grid)
    return cells[0] if cells else None


def degree(grid, row, col):
    """Number of unassigned neighbors (constraints on other free variables)."""
    return sum(1 for (r, c) in NEIGHBORS[(row, col)] if grid[r][c] == 0)


def select_mrv(grid):
    """MRV: cell with the fewest legal values."""
    cells = empty_cells(grid)
    if not cells:
        return None
    return min(cells, key=lambda rc: len(legal_values(grid, *rc)))


def select_mrv_degree(grid):
    """MRV, ties broken by Degree heuristic (most unassigned neighbors)."""
    cells = empty_cells(grid)
    if not cells:
        return None
    return min(cells, key=lambda rc: (len(legal_values(grid, *rc)),
                                      -degree(grid, *rc)))


# ---------------- Value ordering ----------------

def order_default(grid, row, col):
    return legal_values(grid, row, col)


def order_lcv(grid, row, col):
    """LCV: try values that remove the fewest options from neighbors first."""
    def conflicts(num):
        count = 0
        for (r, c) in NEIGHBORS[(row, col)]:
            if grid[r][c] == 0 and is_valid_move(grid, r, c, num):
                count += 1
        return count
    return sorted(legal_values(grid, row, col), key=conflicts)


# ---------------- Backtracking search ----------------

def backtrack(grid, select_var, order_values, stats):
    cell = select_var(grid)
    if cell is None:
        return True  # all variables assigned

    row, col = cell
    for num in order_values(grid, row, col):
        stats["assignments"] += 1
        grid[row][col] = num

        if backtrack(grid, select_var, order_values, stats):
            return True

        # Backtrack
        grid[row][col] = 0
        stats["backtracks"] += 1

    return False


def solve(grid, select_var=select_mrv_degree, order_values=order_lcv):
    stats = {"assignments": 0, "backtracks": 0}
    ok = backtrack(grid, select_var, order_values, stats)
    return ok, stats


def print_grid(grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("| ", end="")
            print(grid[i][j], end=" ")
        print()


grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# " " (Arto Inkala) - shows the heuristics' effect better
hard_grid = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0]
]

METHODS = [
    ("Plain backtracking",  select_first,      order_default),
    ("MRV",                 select_mrv,        order_default),
    ("MRV + Degree",        select_mrv_degree, order_default),
    ("MRV + Degree + LCV",  select_mrv_degree, order_lcv),
]


def compare(puzzle, title):
    print(f"\n=== {title} ===")
    print(f"{'Method':<22}{'Assignments':>12}{'Backtracks':>12}{'Time (ms)':>12}")
    solution = None
    for name, sv, ov in METHODS:
        g = copy.deepcopy(puzzle)
        t0 = time.perf_counter()
        ok, stats = solve(g, sv, ov)
        ms = (time.perf_counter() - t0) * 1000
        if not ok:
            print(f"{name:<22} No solution exists")
            continue
        solution = g
        print(f"{name:<22}{stats['assignments']:>12}{stats['backtracks']:>12}{ms:>12.2f}")

    if solution:
        print("\nSolution:")
        print_grid(solution)


if __name__ == "__main__":
    compare(grid, "Easy sudoku")
    compare(hard_grid, "Hard sudoku")
