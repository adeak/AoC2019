from collections import defaultdict
import numpy as np  # convenience, not necessity
from intcode import Intcode

def parse_outputs(outputs):
    """Parse ascii-encoded output into a board dict"""
    board = defaultdict(lambda:'.')  # '.' is space, '#' is ledge, '^>v<' is robot
    pos = [0,0]
    # using these indices pos[0] is the "left" distance, pos[1] is the "top" distance
    for c in bytes(outputs).decode('ascii'):
        if c == '\n':
            pos[0] += 1
            pos[1] = 0
            continue
        board[tuple(pos)] = c
        if c == '^':
            pos_start = pos.copy()
        pos[1] += 1

    return pos_start, board

def walk_scaffolding(pos_start, board):
    """Walk along scaffolding, find crossings and memorize walk path"""
    rotleft = np.array([[0, -1], [1, 0]])
    rotright = rotleft.T

    # find starting direction for walk
    dirs = {'v': np.array([1, 0]),
            '>': np.array([0, 1]),
            '^': np.array([-1, 0]),
            '<': np.array([0, -1])}
    dir = dirs[board[tuple(pos_start)]]

    # find crossings and path to walk
    crosses = set()
    walkpath = []
    straights = 1  # number of straight steps
    pos = np.array(pos_start)
    while True:
        left = rotleft @ dir
        right = rotright @ dir
        # check if we can step forward
        if board[tuple(pos + dir)] != '#':
            if straights > 1:
                walkpath.append(straights)
                straights = 1
            # check if there's a turn instead
            if board[tuple(pos + left)] == '#':
                # turn left
                pos += left
                dir = left
                walkpath.append('L')
            elif board[tuple(pos + right)] == '#':
                # turn right
                pos += right
                dir = right
                walkpath.append('R')
            else:
                # path is over
                break
        else:
            # we can step forward, so we have to check for crossings now
            if board[tuple(pos + left)] == '#':
                crosses.add(tuple(pos))
            pos += dir
            straights += 1
    return crosses, walkpath

def partition_path(walkpath, max_len=20):
    """Partition the total path list into three "subroutines"

    Assumptions:
        - the first and last subroutine are different
        - subroutines only contain complete "walk along" blocks

    Algorithm:
        - choose an A size, B size and C size within reason
        - define A from the head, B from the tail
        - start matching subsequent pieces, defining C as first needed
        - loop until a valid triple is found

    Since the configuration space is quite limited, even the dumb
    triple loop should finish quite fast.

    Returns: the full input commands to be sent, as bytes
    """

    # longest possible subroutine: uses single digits,
    #     R,0,R,0,R,0,...,R: ceildiv(max_len, 2) items
    # longest possible command: likewise

    for A_len in range(1,-(-max_len//2) + 1):
        A = walkpath[:A_len]
        Astr = ','.join(map(str, A))
        if len(Astr) > max_len:
            break

        for B_len in range(1,-(-max_len//2) + 1):
            B = walkpath[-B_len:]
            Bstr = ','.join(map(str, B))
            if len(Bstr) > max_len:
                # no use going on with B
                break

            for C_len in range(1,-(-max_len//2) + 1):
                found_C_yet = False

                # now keep trying to match the path until failure or success
                # look for C in the process
                subroutines = ['A']
                rest = walkpath[A_len:]
                while rest:
                    if rest[:A_len] == A:
                        sub = 'A'
                        length = A_len
                    elif rest[:B_len] == B:
                        sub = 'B'
                        length = B_len
                    elif not found_C_yet:
                        C = rest[:C_len]
                        Cstr = ','.join(map(str, C))
                        if len(Cstr) > max_len:
                            # no use going on with C
                            break
                        found_C_yet = True
                        sub = 'C'
                        length = C_len
                    elif rest[:C_len] == C:
                        sub = 'C'
                        length = C_len
                    else:
                        # it won't work, go to next combination
                        break
                    subroutines.append(sub)
                    rest = rest[length:]

                    if len(','.join(subroutines)) > max_len:
                        # still won't work
                        break
                else:
                    # we've won!
                    return '\n'.join([','.join(subroutines), Astr, Bstr, Cstr, 'n\n']).encode('ascii')

    # if we're here: we've run out of options
    assert False, 'No solution to the path partitioning!'


def simulate(src, outputs=None):
    if not outputs:
        testing = False

        # live input, simulate board (otherwise take from input)
        comp = Intcode(src)

        while True:
            comp.step()
            if comp.last_op in [None, 'in']:
                break
        outputs = comp.outputs
    else:
        testing = True

    pos_start, board = parse_outputs(outputs)

    crosses, walkpath = walk_scaffolding(pos_start, board)

    # count crossing score
    score = sum(x*y for x,y in crosses)

    for pos in crosses:
        # mark crossings on plot
        board[pos] = 'O'
    print_board(board)  # comment this to stop plotting the board

    # part 2
    commands = partition_path(walkpath)

    if testing:
        # just print the command
        print(commands.decode('ascii'))  # comment this to stop the test command from being printed
        dust = None
    else:
        assert src[0] == 1
        src[0] = 2
        comp = Intcode(src)
        comp.inputs.extend(commands)
        while True:
            comp.step()
            if comp.last_op is None:
                break
        dust = comp.outputs[-1]

    return score, dust

def print_board(board):
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.full(size, fill_value=' ', dtype='U1')
    pixels[tuple((points - mins).T)] = list(board.values())
    print('\n'.join([''.join([c for c in row]) for row in pixels.astype(str)]))
    print()

def day17(inp, testing=False):
    if testing:
        # output is passed as input, don't simulate
        part1 = simulate(None, outputs=inp.encode('ascii'))
    else:
        src = list(map(int, inp.strip().split(',')))
        part1 = simulate(src)

    return part1

if __name__ == "__main__":
    testinp = open('day17.testinp').read()
    print(day17(testinp, testing=True))
    inp = open('day17.inp').read()
    print(day17(inp))
