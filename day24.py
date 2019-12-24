import numpy as np

def step_bugs(board):
    """Step rule for part 1"""
    new_board = board.copy()
    board = board.astype(int)
    neighbs = board[:-2, 1:-1] + board[2:, 1:-1] + board[1:-1, :-2] + board[1:-1, 2:]
    middle = new_board[1:-1, 1:-1]
    living = middle.copy()
    middle[living & (neighbs != 1)] = False
    middle[(~living) & np.isin(neighbs, [1, 2])] = True

    return new_board

def biodiversity(board):
    b = board[1:-1, 1:-1].ravel()
    return (2**np.arange(b.size) * b).sum()

def day24(inp):
    board = np.array([[c == '#' for c in line] for line in inp.splitlines()])

    # pad board with dead bugs
    board = np.pad(board, 1, mode='constant', constant_values=False)

    seens = {board.tobytes()}

    while True:
        board = step_bugs(board)
        b = board.tobytes()
        if b in seens:
            part1 = biodiversity(board)
            return part1
        seens.add(b)

def step_multibugs(boards):
    """Step rule for part 2"""
    new_boards = boards.copy()
    boards = boards.astype(int)

    center = (boards.shape[1] - 2)//2
    mid_from,mid_to =  center - 1, center + 1  # indices in unpadded boards

    # the recipe is weird, just loop
    # and ensure that first and last boards are always empty
    for i, board in enumerate(new_boards):
        b = board.astype(int)
        # original recipe:
        neighbs = b[:-2, 1:-1] + b[2:, 1:-1] + b[1:-1, :-2] + b[1:-1, 2:]
        if i < boards.shape[0] - 1:
            # replace inner values, assume board center is always False
            neighbs[mid_from, center] += boards[i + 1, 1:-1, 1:-1][0, :].sum()
            neighbs[mid_to, center] += boards[i + 1, 1:-1, 1:-1][-1, :].sum()
            neighbs[center, mid_from] += boards[i + 1, 1:-1, 1:-1][:, 0].sum()
            neighbs[center, mid_to] += boards[i + 1, 1:-1, 1:-1][:, -1].sum()
        if i > 0:
            # replace outer values
            neighbs[0, :] += boards[i - 1, 1:-1, 1:-1][mid_from, center].sum()
            neighbs[-1, :] += boards[i - 1, 1:-1, 1:-1][mid_to, center].sum()
            neighbs[:, 0] += boards[i - 1, 1:-1, 1:-1][center, mid_from].sum()
            neighbs[:, -1] += boards[i - 1, 1:-1, 1:-1][center, mid_to].sum()
        middle = board[1:-1, 1:-1]
        living = middle.copy()  # already a bool
        middle[living & (neighbs != 1)] = False
        middle[(~living) & np.isin(neighbs, [1, 2])] = True
        # set middle of middle to False
        middle[center, center] = False

        # decide if we need to expand our 3d padding
        if i == 0:
            # check if this edge level is all dead
            expand_front = int(middle.sum() > 0)
        elif i == boards.shape[0] - 1:
            # same
            expand_end = int(middle.sum() > 0)

    if expand_front or expand_end:
        new_boards = np.pad(new_boards, [(expand_front, expand_end), (0, 0), (0, 0)], mode='constant', constant_values=False)

    return new_boards

def day24b(inp, steps=200):
    board = np.array([[c == '#' for c in line] for line in inp.splitlines()])

    # pad board with dead bugs
    board = np.pad(board, 1, mode='constant', constant_values=False)

    # expand into the multiverse
    boards = np.pad(board[None, ...], [[1], [0], [0]], mode='constant', constant_values=False)  # shape (3, n, n)

    for _ in range(steps):
        boards = step_multibugs(boards)

    return boards.sum()

if __name__ == "__main__":
    testinp = open('day24.testinp').read()
    print(day24(testinp))
    print(day24b(testinp, steps=10))
    inp = open('day24.inp').read()
    print(day24(inp))
    print(day24b(inp))
