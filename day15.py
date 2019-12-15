import numpy as np  # only for printing
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

def find_new_neighbs(oldpos, board, comp, states):
    # all potential neighbours from oldpos:
    candidates = {1: (oldpos[0], oldpos[1] + 1),
                  2: (oldpos[0], oldpos[1] - 1),
                  3: (oldpos[0] - 1, oldpos[1]),
                  4: (oldpos[0] + 1, oldpos[1])}
    # only check unvisited tiles
    candidates = {key:candidate for key,candidate in candidates.items() if candidate not in board}

    valid_neighbs = []
    for dircode,candidate in candidates.items():
        # reload state at oldpos
        comp.import_state(states[oldpos])
        
        # add new direction to inputs
        comp.inputs.append(dircode)

        # simulate until output
        while True:
            comp.step()
            if comp.last_op == 'out':
                res = comp.outputs[-1]
                break

        board[candidate] = res

        # only keep new state if it's not a wall
        if res in (1, 2):
            states[candidate] = comp.export_state()
            valid_neighbs.append(candidate)

    return valid_neighbs

def simulate(src, pos0=(0,0), state=None):
    comp = Intcode(src)
    if not state:
        state = comp.export_state()
    board = {}  # 0 is wall, 1 is visited free, 2 is target
    board[pos0] = -1  # starting point
    states = {pos0: state}  # saves the instuction state for each new point

    to_visit = {pos0}
    for steps in count(1):
        next_visit = set()
        for oldpos in to_visit:
            for nextpos in find_new_neighbs(oldpos, board, comp, states):
                # nextpos is guaranteed to be a new tile
                if board[nextpos] == 2:
                    # part 1
                    print_board(board)
                    return steps, nextpos, states[nextpos]
                next_visit.add(nextpos)
        to_visit = next_visit
        if not to_visit:
            # part 2, watch out for off-by-one (if there's no steps, last step was the last step)
            return steps - 1, None, None

def print_board(board):
    board = {pos: 3 if val == -1 else val for pos,val in board.items()}
    mapping = np.array(['#', ' ', 'x', 'o'])  # 'x' is target, 'o' is initial
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.zeros(size, dtype='U1')
    pixels[tuple(points.T)] = mapping[list(board.values())]  # assume ordered dicts
    print('\n'.join([''.join([c for c in row]) for row in np.rot90(pixels, -1).astype(str)]))
    print()

def day15(inp):
    src = list(map(int, inp.strip().split(',')))

    # find oxygen, save interpreter state for part 2
    part1, pos_O, state = simulate(src)
    part2, _, _ = simulate(src, state=state, pos0=pos_O)

    return part1, part2

if __name__ == "__main__":
    inp = open('day15.inp').read()
    print(day15(inp))
