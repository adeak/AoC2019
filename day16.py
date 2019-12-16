from itertools import cycle, repeat, islice, count
from functools import partial,lru_cache
import numpy as np

# # part 1 native:
# def day16(inp, phases=100):
#     dat = list(map(int, inp.strip()))
#     for phase in range(phases):
#         out = dat.copy()
#         for i in range(len(dat)):
#             patt = islice(cycle(val for k in [0, 1, 0, -1] for val in repeat(k, i + 1)), 1, None)
#             out[i] = int(str(sum(v*p for v,p in zip(dat, patt)))[-1])
#         dat = out
# 
#     return ''.join(map(str, out[:8]))

# part1-2 numpy, too slow for part 2:
def day16(inp, phases=100, part2=False):
    dat = np.array(list(map(int, inp.strip())))
    if part2:
        dat = np.tile(dat, 10000)
    ran = np.arange(dat.size)

    for phase in range(phases):
        out = np.empty_like(dat)
        for i in range(len(dat)):
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
            #print(f'Done with index {i} for phase {phase}...')
        dat = out

        #print(f'Done with phase {phase}/{phases}...')

    if part2:
        # shift msg
        offset = int(map(str, out[:7]))
    else:
        offset = 0

    res = ''.join(map(str, out[offset:offset+8]))

    return res

# def get_index_generators(level):
#     # ones: range(level, 2*level + 1) + n*4*(level+1) for n in count()
#     # minus ones: range(3*(level+1) - 1, 4*(level+1) - 2) + n*4*(level+1) for n in count()
#     plusses = (val + n*4*(level+1) for n in count() for val in range(level, 2*level + 1))
#     minuses = (val + n*4*(level+1) for n in count() for val in range(3*(level+1) - 1, 4*(level+1) - 1))
#     return plusses, minuses
# 
# # part 1 native, recursive; doesn't help:
# def day16(inp, phases=100, part2=False):
#     init = list(map(int, inp.strip()))
# 
#     multi = 10000 if part2 else 1
# 
# #     for k in range(5):
# #         plusses,minuses = get_index_generators(k)
# #         p = [next(plusses) for _ in range(10)]
# #         m = [next(minuses) for _ in range(10)]
# #         print([1 if i in p else -1 if i in m else 0 for i in range(10)])
# #     print()
# #     return
# 
#     @lru_cache(maxsize=None)
#     def request_item(level, index):
#         if level == 0:
#             return init[index % len(init)]
# 
#         plusses,minuses = get_index_generators(index)
#         res = 0
#         for iplus in plusses:
#             if iplus >= multi*len(init):
#                 break
#             res += request_item(level - 1, iplus)
#         for iminus in minuses:
#             if iminus >= multi*len(init):
#                 break
#             res -= request_item(level - 1, iminus)
#         return abs(res) % 10
# 
#     if part2:
#         offset = int(''.join([str(request_item(0, i)) for i in range(7)]))
#     else:
#         offset = 0
# 
#     msg = ''.join([str(request_item(100, i)) for i in range(offset, offset+8)])
# 
#     return msg

if __name__ == "__main__":
    testinp = open('day16.testinp').read()
    print(day16(testinp))
    inp = open('day16.inp').read()
    print(day16(inp))
    #print(day16(inp, part2=True))
