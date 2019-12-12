from itertools import count
from functools import reduce
from math import gcd
import numpy as np

def parse_coords(inp):
    stripped = ''.join([c for c in inp if c not in '[<>=xyz]'])
    dat = [list(map(int, line.split(', '))) for line in stripped.splitlines()]
    return np.array(dat)  # shape (4, 3)

def total_energy(poses, vs):
    return (abs(poses).sum(-1) * abs(vs).sum(-1)).sum()

def lcm(nums):
    """Return the least common multiple of the given numbers"""
    def lcm_pairwise(n, m):
        return (n * m)//gcd(n, m)

    return reduce(lcm_pairwise, nums)

def day12(inp, nt=1000):
    poses = parse_coords(inp)  # shape (4, 3)
    vs = np.zeros_like(poses)

    # check for cycles of individual dimensions, assuming "short" cycles
    # only need to store starting state for this due to uniqueness of the orbits
    # turn equality tests of short arrays to equality tests of short bytes
    initvposes = [poses[:,i].tobytes() + vs[:,i].tobytes() for i in range(3)]
    cycle_lens = [0] * 3

    for t in count(1):
        # part 1
        if t == nt + 1:
            tot_energy = total_energy(poses, vs)

        # apply gravity
        diffs = np.sign(poses[:, None, :] - poses)  # shape (4, 4, 3)
        contribs = diffs.sum(0)
        vs += contribs

        # apply velocity
        poses += vs

        # part 2: check if position + speed was the original one for each dimension
        for i in range(3):
            if cycle_lens[i]:
                # already seen a cycle in this dim
                continue

            vpos = poses[:, i].tobytes() + vs[:, i].tobytes()
            if vpos == initvposes[i]:
                # we've found a cycle in this dimension
                cycle_lens[i] = t

                if all(cycle_lens):
                    # then we're done
                    return tot_energy, lcm(cycle_lens)

if __name__ == "__main__":
    testinp = open('day12.testinp').read()
    print(day12(testinp, nt=100))
    inp = open('day12.inp').read()
    print(day12(inp))
