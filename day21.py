from intcode import Intcode

def simulate(src):
    inputs = '\n'.join([
        'NOT C J',
        'AND D J',
        'NOT A T',
        'OR T J',
        'WALK\n'])
    comp = Intcode(src)
    comp.inputs.extend(inputs.encode('ascii'))

    while True:
        comp.step()
        if comp.last_op is None:
            break
    if comp.outputs[-1] > 255:
        return comp.outputs[-1]

def simulate_part2(src):
    inputs = '\n'.join([
        # jump if D and H are valid
        'OR D T',
        'AND H T',
        'OR T J',

        # except if ABC are all valid
        'NOT A T',
        'NOT T T',
        'AND B T',
        'AND C T',  # T = (A and B and C) now
        'NOT T T',  # T = not (A and B and C)
        'AND T J',

        # always jump if A is empty
        'NOT A T',
        'OR T J',
        'RUN\n'])

    comp = Intcode(src)
    comp.inputs.extend(inputs.encode('ascii'))

    while True:
        comp.step()
        if comp.last_op is None:
            break
    if comp.outputs[-1] > 255:
        return comp.outputs[-1]

def day21(inp):
    src = list(map(int, inp.strip().split(',')))

    part1 = simulate(src)
    part2 = simulate_part2(src)

    return part1,part2

if __name__ == "__main__":
    inp = open('day21.inp').read()
    print(day21(inp))
