import numpy as np
import operator
from itertools import chain, cycle, permutations
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

    def pipe_into(self, other):
        self.pipe = other

    @staticmethod
    def modes_from_op(opval):
        """Decode parameter modes into binary ints"""
        parammodes = chain(map(int, reversed(str(opval//100))), cycle([0])) # 1 for value, 0 for pointer
        return parammodes

    @property
    def next_op(self):
        """Tell what the next input instruction will be without stepping"""
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

class Solver:
    def __init__(self, src):
        self.src = src
        self.choices = []
        self.score = 0
        self.blocks_left = -1

    def find_next_choice(self):
        # first stand still, check where ball exits

        instance = Intcode(self.src)
        instance.inputs.extend(self.choices + [0]*10000)

        steps = 0
        while True:
            instance.step()
            
            if instance.last_op is None:
                break

            if instance.last_op == 'in':
                steps += 1
                #print_board(instance.outputs)
                #input()

        scoreiter = (s for s,y,x in zip(*[reversed(instance.outputs)]*3) if (x,y) == (-1,0))
        next(scoreiter)
        self.score = next(scoreiter)
        self.blocks_left = count_blocks(instance.outputs)
        print(f'blocks left: {self.blocks_left}, score: {self.score}')
        if not self.blocks_left:
            # then we've won
            self.score = next(s for s,y,x in zip(*[reversed(instance.outputs)]*3) if (x,y) == (-1,0))
            return

        # find where the paddle was
        paddlex,paddley = next((x,y) for t,y,x in zip(*[reversed(instance.outputs)]*3) if t == 3)

        # find where the ball was two steps ago
        ballx = next(x for t,y,x in zip(*[reversed(instance.outputs)]*3) if (t,y) == (4, paddley - 1))

        diff = ballx - paddlex
        sign = np.sign(diff)
        buffers = steps - 1 - len(self.choices) - abs(diff)

        # pad with zeros, then take the number of required steps
        self.choices.extend([0] * buffers + [sign] * abs(diff))
        
        return


def count_blocks(outputs):
    board = {(x,y):t for x,y,t in zip(*[iter(outputs)]*3) if (x,y) != (-1,0)}
    return sum(1 for typ in board.values() if typ == 2)

def print_board(outputs):
    mapping = np.array([' ', '=', '#', '\N{em dash}', 'o'])
    board = {(x,y):t for x,y,t in zip(*[iter(outputs)]*3) if (x,y) != (-1,0)}
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.zeros(size, dtype='U1')
    pixels[tuple(points.T)] = mapping[list(board.values())]  # assume ordered dicts
    print('\n'.join([''.join([c for c in row]) for row in np.rot90(pixels, -1).astype(str)]))

def simulate_part1(src, choices=[]):
    instance = Intcode(src)
    instance.inputs.extend(choices)

    while True:
        instance.step()

        # break if exit
        if instance.last_op is None:
            break

        ## stop if input is requested in the next step
        #if instance.next_op == 'in':
        #    print_board(instance.outputs)
        #    input()

    return count_blocks(instance.outputs)

def simulate_part2(src):
    src[0] = 2

    solver = Solver(src)
    while solver.blocks_left:
        solver.find_next_choice()
    return solver.score
    #simulate_part1(src, solver.choices)

def day13(inp):
    src = list(map(int, inp.strip().split(',')))

    part1 = simulate_part1(src)
    part2 = simulate_part2(src)

    return part1,part2

if __name__ == "__main__":
    inp = open('day13.inp').read()
    print(day13(inp))
    # 10227 too low
