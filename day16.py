from itertools import cycle, repeat, islice, count
from functools import partial,lru_cache
import numpy as np

# part1-2 numpy, too slow for part 2:
def day16(inp, phases=100):
    init = np.array(list(map(int, inp.strip())))
    dat = init
    ran = np.arange(dat.size)

    for phase in range(phases):
        out = np.empty_like(dat)
        for i in range(dat.size):
            # [0, 1, 0, -1]: ones = [1] + k*4 -> shift -1: [0] + k*4
            # [0, 0, 1, 1, 0, 0, -1, -1]: ones = [2, 3] + k*8 -> shift -1: [1, 2] + k*8
            # [0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1]: ones = [3, 4, 5] + k*16 -> shift -1: [2, 3, 4] + k*12
            # [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1]: ones = [4, 5, 6, 7] + k*16 -> shift -1: [3, 4, 5, 6] + k*16
            #
            # [0, 1, 0, -1]: minusones = [3] + k*4 -> shift -1: [2] + k*4
            # [0, 0, 1, 1, 0, 0, -1, -1]: minusones = [6, 7] + k*8 -> shift -1: [5, 6] + k*8
            # [0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1]: minusones = [9, 10, 11] + k*16 -> shift -1: [8, 9, 10] + k*12

            ranmod = ran % (4*(i+1))
            ones = (i <= ranmod) & (ranmod <= 2*i)
            minusones = (3*(i+1) - 1 <= ranmod) & (ranmod <= 4*(i+1) - 2)
            out[i] = abs(dat[ones].sum() - dat[minusones].sum()) % 10
        dat = out

    res = ''.join(map(str, out[:8]))

    return res

def day16b(inp, phases=100):
    init = np.array(list(map(int, inp.strip())))
    dat = np.tile(init, 10000)

    # assume that the requested bits are always in the tail
    # where the mapping matrix is trivial (upper triangular with full ones)
    offset = int(''.join(map(str, init[:7])))
    half = dat.size//2
    assert offset >= half

    for phase in range(phases):
        out = np.empty_like(dat)
        out[-1:half-1:-1] = abs(dat[-1:half-1:-1].cumsum()) % 10
        dat = out

    res = ''.join(map(str, out[offset:offset+8]))

    return res

if __name__ == "__main__":
    testinp = open('day16.testinp').read()
    print(day16(testinp))
    inp = open('day16.inp').read()
    print(day16(inp))
    print(day16b(inp))
