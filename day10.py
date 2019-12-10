from math import gcd
from itertools import count
from collections import defaultdict
import numpy as np

def find_visibles(dat, allpos, maxsize, inds):
    x0,y0 = inds
    others = allpos - {(x0,y0)}
    visibles = others.copy()
    for x,y in others:
        delta = x - x0, y - y0
        divs = gcd(*delta)
        atomic_delta = delta[0]//divs, delta[1]//divs
        for n in count(divs + 1):
            blockee = x0 + atomic_delta[0]*n, y0 + atomic_delta[1]*n
            if not (0 <= blockee[0] < maxsize[0] and 0 <= blockee[1] < maxsize[1]):
                break
            if blockee in visibles:
                visibles.remove(blockee)

    return len(visibles)

def do_laser_thing(dat, allpos, maxsize, inds):
    x0,y0 = inds
    others = allpos - {(x0,y0)}
    blockerdat = defaultdict(set)

    # construct blocker mapping
    for x,y in others:
        delta = x - x0, y - y0
        divs = gcd(*delta)
        atomic_delta = delta[0]//divs, delta[1]//divs
        for n in count(divs + 1):
            blockee = x0 + atomic_delta[0]*n, y0 + atomic_delta[1]*n
            if not (0 <= blockee[0] < maxsize[0] and 0 <= blockee[1] < maxsize[1]):
                break
            if blockee in others:
                # (x,y) blocks blockee
                blockerdat[blockee].add((x,y))

    laserdir = np.pi/2 + 1e-8  # pointing up (almost)
    for shot in count(1):
        visibles = [blockee for blockee in others if not blockerdat[blockee]]
        adirs = [np.arctan2(- visible[0] + x0, visible[1] - y0) for visible in visibles]
        for i,adir in enumerate(adirs):
            while adir >= laserdir:
                adir -= 2*np.pi
            adirs[i] = adir
        next_ind = np.argmax(adirs)
        next_hit = visibles[next_ind]
        laserdir = adirs[next_ind]
        if shot == 200:
            return next_hit[1]*100 + next_hit[0]
        blockerdat.pop(next_hit)
        for blockee,blockers in blockerdat.items():
            blockers -= {next_hit}
        others.remove(next_hit)

def day10(inp):
    dat = np.array([[c == "#" for c in row] for row in inp.strip().split('\n')])

    allpos = set(zip(*dat.nonzero()))
    maxsize = dat.shape
    most = 0
    for inds in allpos:
        visibles = find_visibles(dat, allpos, maxsize, inds)
        if visibles > most:
            bestpos = inds
            most = visibles
    part1 = most

    part2 = do_laser_thing(dat, allpos, maxsize, bestpos)

    return part1,part2

if __name__ == "__main__":
    testinp = open('day10.testinp').read()
    print(day10(testinp))
    inp = open('day10.inp').read()
    print(day10(inp))
