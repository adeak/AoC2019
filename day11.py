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

def simulate(src, part1=True):
    instance = Intcode(src)
    board = defaultdict(int)
    pos = (0, 0)
    dir = (-1, 0)

    if not part1:
        board[pos] = 1

    while True:
        # loop over pixels
        instance.inputs.append(board[pos])

        # loop over instruction steps until two outputs or exit
        while len(instance.outputs) < 2:
            instance.step()

            if instance.last_op is None:
                # we're done
                if part1:
                    # return colored pixels
                    return len(board)
                else:
                    # return picture
                    print_picture(board)
                    return

        pixel, dirval = instance.outputs
        instance.outputs.clear()

        board[pos] = pixel  # paint
        dir = (dir[1], -dir[0]) if dirval else (-dir[1], dir[0])  # rotate
        pos = pos[0] + dir[0], pos[1] + dir[1]  # step

def print_picture(board):
    minx = min(board, key=operator.itemgetter(0))[0]
    maxx = max(board, key=operator.itemgetter(0))[0]
    miny = min(board, key=operator.itemgetter(1))[1]
    maxy = max(board, key=operator.itemgetter(1))[1]
    print('\n'.join([''.join(['#' if board[i,j] else ' ' for j in range(miny, maxy + 1)]) for i in range(minx, maxx + 1)]))

def day11(inp):
    src = list(map(int, inp.strip().split(',')))

    part1 = simulate(src)
    simulate(src, part1=False)

    return part1

if __name__ == "__main__":
    inp = open('day11.inp').read()
    print(day11(inp))
