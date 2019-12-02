import operator
import itertools

def step_intcode(src, i):
    """Take a step in an intcode program

    Input:
        src: list of ints with instructions
          i: current position of instruction pointer

    Returns in a tuple:
         op: function to call or None for exit
     params: the operands for op if any, else []
      i_out: index of the output if any, else None
          i: the next index of the instruction pointer
    """

    ops = {1: operator.add,
           2: operator.mul,
           99: None,  # signal exit
           }

    opcode = src[i]
    if opcode == 99:
        n_inps = 0
        n_outs = 0
    elif opcode in [1, 2]:
        n_inps = 2
        n_outs = 1
    else:
        assert False, f'Invalid opcode {opcode} at position {i}!'

    op = ops.get(opcode, -1)
    assert op != -1, f'Need to implement more operations in ops dict!'

    params = [src[src[k]] for k in range(i + 1, i + 1 + n_inps)]
    i_out = src[i + 1 + n_inps] if n_outs else None
    i += 1 + n_inps + n_outs

    return op, params, i_out, i


def day02(inp, nounverb=(12, 2)):
    src = list(map(int, inp.strip().split(',')))

    if nounverb:
        src[1],src[2] = nounverb
    
    i = 0
    while True:
        op, params, i_out, i = step_intcode(src, i)
        if not op:
            # exit
            break
        
        src[i_out] = op(*params)
    return src[0]

def day02b(inp):
    for n,v in itertools.product(range(100), repeat=2):
        if day02(inp, nounverb=(n,v)) == 19690720:
            return 100 * n + v
    assert False, 'No day 2 solution...'

if __name__ == "__main__":
    testinp = open('day02.testinp').read()
    print(day02(testinp, nounverb=None))
    inp = open('day02.inp').read()
    print(day02(inp))
    print(day02b(inp))
