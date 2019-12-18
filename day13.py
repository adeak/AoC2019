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
            assert False, f'Invalid opcode {opcode} at position {ip}!'
    
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
        self.choices = []  # correct inputs to the intcode program
        self.score = 0
        self.simulating = False  # flipped to True once there's an input
        self.total_blocks = None  # number of initial blocks; part 1
        self.blocks_left = -1  # countdown until end of game
        self.idle_steps = 10  # incremented steps to stand in one place for the next move
        self.checkpoint = None  # state of the interpreter in a safe state
        self.steps = 0  # steps taken for checkpoint
        self.paddley = None  # constant y position of the paddle

    def find_next_choice(self):
        # first stand still, check where ball exits
        instance = Intcode(self.src)
        if self.checkpoint:
            # load state from checkpoint
            instance.import_state(self.checkpoint)

        # but always override inputs (checkpoint inputs are noisy due to idle steps)
        instance.inputs.clear()
        instance.inputs.extend(self.choices[self.steps:] + [0]*self.idle_steps)

        steps = self.steps
        while True:
            try:
                instance.step()
            except IndexError:
                # retry with more steps of standing still
                self.idle_steps *= 10
                return
            
            if instance.last_op is None and steps > self.steps:
                break

            if not self.simulating and instance.last_op == 'in':
                self.simulating = True
                # count number of initial blocks
                self.total_blocks = count_blocks(instance.outputs)

                # assumption: paddle y component is constant, store that too
                self.paddley = next(y for t,y,x in zip(*[reversed(instance.outputs)]*3) if t == 3)

            if instance.last_op == 'in':
                # check state when input is requested for consistent ball-and-paddle state
                steps += 1

                ballx,bally = next((x,y) for t,y,x in zip(*[reversed(instance.outputs)]*3) if t == 4 and (x,y) != (-1,0))


                # check if we hit it; if yes: checkpoint
                if bally == self.paddley - 1:
                    paddlex = next(x for t,y,x in zip(*[reversed(instance.outputs)]*3) if t == 3 and (x,y) != (-1,0))

                    if ballx == paddlex:
                        self.checkpoint = instance.export_state()
                        self.steps = steps
                        self.choices = (self.choices + [0]*self.idle_steps)[:self.steps]
                        return

        self.blocks_left = count_blocks(instance.outputs)
        if not self.blocks_left:
            # then we've won, need final score
            self.score = next(s for s,y,x in zip(*[reversed(instance.outputs)]*3) if (x,y) == (-1,0))
            return

        # find where the paddle was when we died
        paddlex = next(x for t,y,x in zip(*[reversed(instance.outputs)]*3) if t == 3 and (x,y) != (-1,0))

        # find where the ball was above the paddle's level
        ballx = next(x for t,y,x in zip(*[reversed(instance.outputs)]*3) if (t,y) == (4, self.paddley - 1))

        diff = ballx - paddlex
        sign = np.sign(diff)
        buffers = steps - self.steps - 1 - len(self.choices) - abs(diff)

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

def day13(inp):
    src = list(map(int, inp.strip().split(',')))
    src[0] = 2

    solver = Solver(src)
    while solver.blocks_left:
        solver.find_next_choice()

    return solver.total_blocks, solver.score

if __name__ == "__main__":
    inp = open('day13.inp').read()
    print(day13(inp))
