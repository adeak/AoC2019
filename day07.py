import operator
from itertools import chain, cycle, permutations
from collections import deque

class Intcode:
    ops = {1: operator.add,
           2: operator.mul,
           3: 'in',
           4: 'out',
           5: 'jmpif',
           6: 'jmpifn',
           7: lambda i,j: int(i < j),
           8: lambda i,j: int(i == j),
           99: None,  # signal exit
           }

    def __init__(self, src, inputs=None):
        self.src = src.copy()
        self.ip = 0
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
        else:
            assert False, f'Invalid opcode {opcode} at position {i}!'
    
        op = self.ops.get(opcode, -1)
        assert op != -1, f'Need to implement more operations in ops dict!'

        self.last_op = op
    
        # get position of output, if any
        ip_out = src[ip + 1 + n_inps] if n_outs else None

        # handle "input": no parameter modes
        if op == "in":
            src[ip_out] = self.inputs.popleft()
    
        parammodes = self.modes_from_op(opval)
        params = [src[k] if mode else src[src[k]] for k,mode in zip(range(ip + 1, ip + 1 + n_inps), parammodes)]

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

def simulate_sequence(src, seq, part1=True):
    instances = [Intcode(src) for _ in range(5)]

    # initialize inputs with phase, connect instances
    for i_amp,(instance,phase) in enumerate(zip(instances, seq)):
        instance.inputs.append(phase)
        instance.pipe_into(instances[(i_amp + 1) % 5])
    instances[0].inputs.append(0)

    while True:
        # loop over feedback loops
        for i_amp,instance in enumerate(instances):
            # loop over amplifiers
            while True:
                # loop over instruction steps
                instance.step()
        
                if instance.last_op is None:
                    # exit this sequence for good, read last output (part 2)
                    return instances[-1].outputs[-1]
        
                if instance.last_op == 'out':
                    # hand execution over to the next amplifier
                    break

        if part1:
            return instances[-1].outputs[-1]

def day07(inp):
    src = list(map(int, inp.strip().split(',')))

    part1 = max(simulate_sequence(src, seq) for seq in permutations(range(5)))
    part2 = max(simulate_sequence(src, seq, part1=False) for seq in permutations(range(5, 10)))

    return part1, part2


if __name__ == "__main__":
    testinp = open('day07.testinp').read()
    print(day07(testinp))
    inp = open('day07.inp').read()
    print(day07(inp))
