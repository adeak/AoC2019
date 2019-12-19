from itertools import product,count
import numpy as np  # only for plotting
from intcode import Intcode

def get_traction(src, x, y):
    comp = Intcode(src)

    comp.inputs.extend([x, y])
    while True:
        comp.step()
        if comp.last_op == 'out':
            return comp.outputs[-1]

def print_board(board):
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.full(size, fill_value=' ', dtype='U1')
    pixels[tuple((points - mins).T)] = list(board.values())
    print('\n'.join([''.join([c for c in row]) for row in pixels.T.astype(str)]))
    print()

def day19(inp, patchsize=50, findsize=100):
    src = list(map(int, inp.strip().split(',')))

    # manually special-case top 3x3 where there's a hole,
    # assume no more holes
    # optimization: slope of width vs row is ~ 1/3

    tracts = 1  # (0,0)
    board = {(0,0): 1}  # position -> type
    bounds = {1: [3, None]}  # row -> [from, to] (dummy initial value for first checked row)

    for y in count(2):
        # part 1
        if 2 < y < 51:
            prev_bounds = bounds[y - 1]
            prev_tracts = max(0, min(patchsize - 1, prev_bounds[1]) - prev_bounds[0] + 1)
            tracts += prev_tracts

        x = bounds[y - 1][0]
        while True:
            is_tract = get_traction(src, x, y)
            board[x,y] = is_tract

            if y in bounds and not is_tract and (x-1,y) not in board:
                # then we've overshot in x
                x -= 1
                continue
            elif y in bounds and not is_tract and board[x - 1, y] == 1:
                # we've found an edge, start next row
                bounds[y].append(x - 1)

                # but check for shipsize first for part 2
                if y > min(bounds) + findsize and  bounds[y - findsize + 1][1] >= bounds[y][0] + findsize - 1:
                    # then we can fit the ship in, done
                    x0,y0 = bounds[y][0], y - findsize + 1
                    return tracts, 10000*x0 + y0
                break

            if y not in bounds and is_tract:
                # we've found the start of a block
                bounds[y] = [x]

                # now we can estimate the next x from 1/3 slope
                x += y // 3
            elif y not in bounds or (y in bounds and is_tract):
                # we need to step right either to find the start or to find the end
                x += 1
            else:
                assert False, 'Impossible case found...'

if __name__ == "__main__":
    inp = open('day19.inp').read()
    print(day19(inp))
