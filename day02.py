import itertools

def day02(inp, nounverb=(12, 2)):
    src = list(map(int, inp.strip().split(',')))

    if nounverb:
        src[1],src[2] = nounverb
    
    i = 0
    while True:
        op = src[i]
        if op == 99:
            break
        if op in [1, 2]:
            in1,in2 = src[src[i + 1]], src[src[i + 2]]
            i_out = src[i + 3]
            i += 4
            if op == 1:
                res = in1 + in2
            elif op == 2:
                res = in1 * in2
            else:
                assert False, 'Implement more ops!'
            src[i_out] = res
            continue
        assert False, f'Invalid opcode {op} at position {i}!'
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
