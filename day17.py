import numpy as np  # convenience, not necessity
import operator
from itertools import chain, cycle, count
from collections import deque, defaultdict

class Intcode:
    ops = {1: operator.add,
           2: operator.mul,
           3: 'in',
           4: 'out',
           5: 'jmpif',
           6: 'jmpifn',
           7: lambda i,j: int(i < j),
           8: lambda i,j: int(i == j),
           9: 'rebase',
           99: None,  # signal exit
           }

    def __init__(self, src, inputs=None):
        self.src = defaultdict(int)
        self.src.update(enumerate(src))
        self.ip = 0
        self.base = 0
        self.pipe = None  # potential instance to pipe output into
        if not inputs:
            inputs = deque([])
        self.inputs = deque(inputs)
        self.outputs = []
        self.last_op = None

    def export_state(self):
        return self.src.copy(), self.ip, self.base, self.inputs.copy(), self.outputs.copy(), self.last_op

    def import_state(self, state):
        src, self.ip, self.base, inputs, outputs, self.last_op = state
        self.src = src.copy()
        self.inputs = inputs.copy()
        self.outputs = outputs.copy()

    def pipe_into(self, other):
        self.pipe = other

    @staticmethod
    def modes_from_op(opval):
        """Decode parameter modes into binary ints"""
        parammodes = chain(map(int, reversed(str(opval//100))), cycle([0])) # 1 for value, 0 for pointer
        return parammodes

    @property
    def next_op(self):
        """Peek at the next input instruction"""
        return self.ops[self.src[self.ip] % 100]

    def step(self):
        """Take a step in the intcode program"""
        src = self.src
        ip = self.ip
    
        opval = src[ip]
    
        opcode = opval % 100
        if opcode == 99:
            n_inps = 0
            n_outs = 0
        elif opcode in [1, 2]:
            n_inps = 2
            n_outs = 1
        elif opcode == 3:
            n_inps = 0
            n_outs = 1
        elif opcode == 4:
            n_inps = 1
            n_outs = 0
        elif opcode in [5, 6]:
            n_inps = 2
            n_outs = 0
        elif opcode in [7, 8]:
            n_inps = 2
            n_outs = 1
        elif opcode == 9:
            n_inps = 1
            n_outs = 0
        else:
            assert False, f'Invalid opcode {opcode} at position {i}!'
    
        op = self.ops.get(opcode, -1)
        assert op != -1, f'Need to implement more operations in ops dict!'

        self.last_op = op
    
        parammodes = self.modes_from_op(opval)
        params = []
        for k,mode in zip(range(ip + 1, ip + 1 + n_inps), parammodes):
            if mode == 0:
                index = src[k]
            elif mode == 1:
                index = k
            elif mode == 2:
                index = self.base + src[k]
            else:
                assert False, f'Invalid parameter mode {mode}!'
            assert index >= 0, f'Invalid input index {index}!'

            param = src[index]
            params.append(param)

        if n_outs:
            output_mode = next(parammodes)
            if output_mode == 0:
                ip_out = src[ip + 1 + n_inps]
            elif output_mode == 2:
                ip_out = self.base + src[ip + 1 + n_inps]
            else:
                assert False, 'What does output_mode == 1 mean?'

            assert ip_out >= 0, f'Invalid output index {ip_out}!'
        else:
            ip_out = None

        # handle "input"
        if op == "in":
            src[ip_out] = self.inputs.popleft()

        # handle relative base offset
        if op == 'rebase':
            offset = params[0]
            self.base += offset

        # handle jumps, increment intruction pointer
        if (op == 'jmpif' and params[0]) or (op == 'jmpifn' and not params[0]):
            self.ip = params[1]
        else:
            self.ip += 1 + n_inps + n_outs
    
        # handle "output"
        if op == "out":
            # value is params[0]
            res = params[0]
            self.outputs.append(res)
            if self.pipe:
                self.pipe.inputs.append(res)
    
        # compute values for callables
        if callable(op):
            src[ip_out] = op(*params)

        return


def simulate(src):
    comp = Intcode(src)
    board = defaultdict(lambda:'.')  # '.' is space, '#' is ledge, '^>v<' is robot

    while True:
        comp.step()
        if comp.last_op in [None, 'in']:
            break

    pos = [0,0]
    # using these indices pos[0] is the "left" distance, pos[1] is the "top" distance
    for o in comp.outputs:
        c = chr(o)
        if c == '\n':
            pos[0] += 1
            pos[1] = 0
            continue
        board[tuple(pos)] = c
        if c == '^':
            pos_start = pos.copy()
        pos[1] += 1

    rotleft = np.array([[0, -1], [1, 0]])
    rotright = rotleft.T

    # find starting direction for walk
    dir = np.array([1, 0])
    while board[tuple(pos_start + dir)] != '#':
        dir = rotleft @ dir

    # find crossings
    crosses = set()
    pos = np.array(pos_start)
    while True:
        left = rotleft @ dir
        right = rotright @ dir
        # check if we can step forward
        if board[tuple(pos + dir)] != '#':
            # check if there's a turn instead
            if board[tuple(pos + left)] == '#':
                # turn left
                pos += left
                dir = left
            elif board[tuple(pos + right)] == '#':
                # turn right
                pos += right
                dir = right
            else:
                # path is over
                break
        else:
            # we can step forward, so we have to check for crossings now
            if board[tuple(pos + left)] == '#':
                crosses.add(tuple(pos))
            pos += dir

    # count crossing score
    score = sum(x*y for x,y in crosses)

    for pos in crosses:
        # mark crossings on plot
        board[pos] = 'O'
    print_board(board)

    return score

def print_board(board):
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.full(size, fill_value=' ', dtype='U1')
    pixels[tuple((points - mins).T)] = list(board.values())
    print('\n'.join([''.join([c for c in row]) for row in pixels.astype(str)]))
    print()

def day17(inp):
    src = list(map(int, inp.strip().split(',')))

    part1 = simulate(src)

    return part1

if __name__ == "__main__":
    inp = open('day17.inp').read()
    print(day17(inp))
