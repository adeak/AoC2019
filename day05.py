import operator
from itertools import chain, cycle

def step_intcode(src, i, incode):
    """Take a step in an intcode program

    Input:
        src: list of ints with instructions
          i: current position of instruction pointer
     incode: value for input instruction

    Returns in a tuple:
         op: str, function to call or None for exit
     params: the operands for op if any, else []
      i_out: index of the output if any, else None
          i: the next index of the instruction pointer
    """

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

    opval = src[i]

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

    op = ops.get(opcode, -1)
    assert op != -1, f'Need to implement more operations in ops dict!'

    # decode parameter modes into binary ints
    parammodes = chain(map(int, reversed(str(opval//100))), cycle([0])) # 1 for value, 0 for pointer

    if op == "in":
        params = [incode]
    else:
        params = [src[k] if mode else src[src[k]] for k,mode in zip(range(i + 1, i + 1 + n_inps), parammodes)]

    i_out = src[i + 1 + n_inps] if n_outs else None

    # handle jumps first, otherwise increment instruction pointer
    if (op == 'jmpif' and params[0]) or (op == 'jmpifn' and not params[0]):
        i = params[1]
    else:
        i += 1 + n_inps + n_outs

    return op, params, i_out, i

def day05(inp, incode=1):
    src = list(map(int, inp.strip().split(',')))

    i = 0
    while True:
        op, params, i_out, i = step_intcode(src, i, incode)

        if op is None:
            # exit, should never happen
            assert False, 'Code exited without nonzero output!'

        if op == 'out':
            # output is in params[0]
            out = params[0]
            if out:
                return out
            continue

        if op in ['jmpif', 'jmpifn']:
            # i already incremented
            continue

        if op == 'in':
            # input is in params[0]
            res = params[0]
        else:
            # compute result; add/mul/lt/eq cases
            res = op(*params)

        src[i_out] = res

if __name__ == "__main__":
    inp = open('day05.inp').read()
    print(day05(inp))  # part 1
    print(day05(inp, incode=5))  # part 2
