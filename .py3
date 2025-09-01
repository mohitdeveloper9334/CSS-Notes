from collections import deque
import sys

def read_input():
    data = sys.stdin.read().strip().split()
    if not data:
        return None
    it = iter(data)
    M = int(next(it)); N = int(next(it))
    grid = []
    for _ in range(M):
        row = []
        for _ in range(N):
            row.append(next(it))
        grid.append(row)
    return M, N, grid

def find_sofa(grid, M, N, ch):
    # find two cells marked ch (either 's' or 'S') and return anchor + orientation
    positions = [(i,j) for i in range(M) for j in range(N) if grid[i][j] == ch]
    if len(positions) != 2:
        return None
    (r1,c1),(r2,c2) = positions
    # horizontal?
    if r1 == r2 and abs(c1-c2) == 1:
        # anchor is left-most (r, min_c)
        r = r1; c = min(c1,c2)
        return (r, c, 'H')
    # vertical?
    if c1 == c2 and abs(r1-r2) == 1:
        r = min(r1,r2); c = c1
        return (r, c, 'V')
    return None

def in_bounds(r,c,M,N):
    return 0 <= r < M and 0 <= c < N

def cell_free(grid, r, c):
    # free if not 'H'
    return grid[r][c] != 'H'

def valid_H_anchor(grid, r, c, M, N):
    # anchor for H must have c+1 valid
    return in_bounds(r,c,M,N) and in_bounds(r,c+1,M,N) and cell_free(grid,r,c) and cell_free(grid,r,c+1)

def valid_V_anchor(grid, r, c, M, N):
    # anchor for V must have r+1 valid
    return in_bounds(r,c,M,N) and in_bounds(r+1,c,M,N) and cell_free(grid,r,c) and cell_free(grid,r+1,c)

def bfs_min_steps(M, N, grid, start, target):
    if start is None or target is None:
        return None
    # visited: set of (r,c,orient)
    q = deque()
    q.append((start[0], start[1], start[2], 0))
    visited = set([(start[0], start[1], start[2])])

    while q:
        r, c, orient, dist = q.popleft()
        # check goal
        if (r, c, orient) == target:
            return dist

        # generate shift moves
        if orient == 'H':
            # Up: check (r-1,c) and (r-1,c+1)
            nr = r-1; nc = c
            if nr >= 0 and cell_free(grid, nr, nc) and cell_free(grid, nr, nc+1):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Down: check (r+1,c) and (r+1,c+1)
            nr = r+1; nc = c
            if r+1 < M and cell_free(grid, nr, nc) and cell_free(grid, nr, nc+1):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Left: check (r,c-1)
            nr = r; nc = c-1
            if nc >= 0 and cell_free(grid, nr, nc):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Right: check (r,c+2)
            nr = r; nc = c+1
            if c+2-1 < N and c+2 < N: # simplified below
                pass
            # Right simpler:
            nr = r; nc = c+1
            if c+1 < N and cell_free(grid, nr, nc+1): # c+2 cell exists and free
                # but careful: want to ensure new anchor at (r,c+1) has cells (r,c+1),(r,c+2) -> need c+2 < N
                if c+2 < N and cell_free(grid, nr, nc+0): # check (r,c+1) itself already implied; check (r,c+2)
                    # however the previous conditional messy; rewrite properly below
                    pass

        # We'll instead implement shifts with clean bounds checks per orientation below
        break

    # Because above got messy, implement fresh BFS cleanly:
    q = deque()
    q.append((start[0], start[1], start[2], 0))
    visited = set([(start[0], start[1], start[2])])

    while q:
        r, c, orient, dist = q.popleft()
        if (r, c, orient) == target:
            return dist

        if orient == 'H':
            # ensure anchor is valid (safety)
            if not valid_H_anchor(grid, r, c, M, N):
                continue
            # Up
            nr = r-1; nc = c
            if nr >= 0 and cell_free(grid, nr, nc) and cell_free(grid, nr, nc+1):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Down
            nr = r+1; nc = c
            if r+1 < M and cell_free(grid, nr, nc) and cell_free(grid, nr, nc+1):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Left
            nr = r; nc = c-1
            if nc >= 0 and cell_free(grid, nr, nc):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))
            # Right
            nr = r; nc = c+1
            # new anchor (r,c+1) must be valid: need c+2 < N and both cells free
            if c+2 < N and cell_free(grid, r, c+1) and cell_free(grid, r, c+2):
                state = (nr, nc, 'H')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'H', dist+1))

            # Rotations: two possible 2x2 blocks that include current horizontal sofa:
            # top-left at (r, c) and top-left at (r-1, c)
            # For each complete 2x2 free, we can rotate to two vertical anchors.
            # block at (r, c)
            for bi in (r, r-1):
                bj = c
                if 0 <= bi < M-1 and 0 <= bj < N-1:
                    cells = [(bi,bj),(bi,bj+1),(bi+1,bj),(bi+1,bj+1)]
                    if all(cell_free(grid, x,y) for (x,y) in cells):
                        # possible vertical anchors: (bi, bj) and (bi, bj+1)
                        v1 = (bi, bj, 'V')
                        v2 = (bi, bj+1, 'V')
                        if v1 not in visited:
                            visited.add(v1); q.append((v1[0], v1[1], 'V', dist+1))
                        if v2 not in visited:
                            visited.add(v2); q.append((v2[0], v2[1], 'V', dist+1))

        else: # orient == 'V'
            if not valid_V_anchor(grid, r, c, M, N):
                continue
            # Up
            nr = r-1; nc = c
            if nr >= 0 and cell_free(grid, nr, nc):
                # need nr and nr+1 -> nr+1 is r
                if cell_free(grid, nr, nc) and cell_free(grid, nr+1, nc):
                    state = (nr, nc, 'V')
                    if state not in visited:
                        visited.add(state); q.append((nr, nc, 'V', dist+1))
            # Down
            nr = r+1; nc = c
            # new anchor r+1 must satisfy r+2 < M and both free
            if r+2 < M and cell_free(grid, r+1, c) and cell_free(grid, r+2, c):
                state = (nr, nc, 'V')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'V', dist+1))
            # Left
            nr = r; nc = c-1
            if nc >= 0 and cell_free(grid, r, nc) and cell_free(grid, r+1, nc):
                state = (nr, nc, 'V')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'V', dist+1))
            # Right
            nr = r; nc = c+1
            if c+1 < N and cell_free(grid, r, c+1) and cell_free(grid, r+1, c+1):
                state = (nr, nc, 'V')
                if state not in visited:
                    visited.add(state); q.append((nr, nc, 'V', dist+1))

            # Rotations: two possible 2x2 blocks including current vertical sofa:
            # top-left at (r, c) and top-left at (r, c-1)
            for bi, bj in ((r, c), (r, c-1)):
                if 0 <= bi < M-1 and 0 <= bj < N-1:
                    cells = [(bi,bj),(bi,bj+1),(bi+1,bj),(bi+1,bj+1)]
                    if all(cell_free(grid, x,y) for (x,y) in cells):
                        # possible horizontal anchors: (bi, bj) and (bi+1, bj)
                        h1 = (bi, bj, 'H')
                        h2 = (bi+1, bj, 'H')
                        if h1 not in visited:
                            visited.add(h1); q.append((h1[0], h1[1], 'H', dist+1))
                        if h2 not in visited:
                            visited.add(h2); q.append((h2[0], h2[1], 'H', dist+1))

    return None

def main():
    inp = read_input()
    if inp is None:
        return
    M, N, grid = inp
    start = find_sofa(grid, M, N, 's')
    target = find_sofa(grid, M, N, 'S')

    # treat all non-'H' cells as free (s and S are considered free already by cell_free)
    res = bfs_min_steps(M, N, grid, start, target)
    if res is None:
        print("Impossible")
    else:
        print(res)

if __name__ == "__main__":
    main()

