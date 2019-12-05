import numpy as np

def print_wires(origin, wires):
    out = np.full(wires.shape[1:], fill_value='.')
    for i,layer in enumerate(wires, 1):
        out[layer] = str(i)
    out[origin[0], origin[1]] = 'o'

    print('\n'.join([''.join([c for c in row]) for row in out.T[::-1]]))


def get_wires(inp):
    """Return the origin position and an array of wires of shape (2,posx,posy)"""

    rows = []
    for line in inp.splitlines():
        words = line.split(',')
        pos = np.zeros((1, 2), dtype=int)
        row = [pos]
        for word in words:
            dir,length = word[0], int(word[1:])
            piece = np.zeros((length, 2), dtype=int)
            l = np.arange(1, length + 1)
            if dir == 'R':
                piece[:, 0] = l
            elif dir == 'L':
                piece[:, 0] = -l
            elif dir == 'U':
                piece[:, 1] = l
            elif dir == 'D':
                piece[:, 1] = -l
            else:
                assert False, f'Invalid direction {dir}!'
            row.append(pos + piece)
            pos += piece[-1, :]
        rows.append(np.concatenate(row))

    # find common bounding box, construct ndarray with shape (nwire, posx, posy)
    minvals = np.min([row.min(0) for row in rows], 0)
    maxvals = np.max([row.max(0) for row in rows], 0)

    size = (len(rows), maxvals[0] - minvals[0] + 1, maxvals[1] - minvals[1] + 1)
    origin = -minvals
    wires = np.zeros(size, dtype=bool)
    # True where there's a wire, False where there's none
    for i,row in enumerate(rows):
        shifted = row - minvals
        wires[i, shifted[:, 0], shifted[:, 1]] = True

    return origin,wires

def get_pathlengths(inp, origin, wires):
    """Brute force path length computer, needs a double array under the hood, too much memory"""

    lengths = np.full(wires.shape, fill_value=np.inf)  # shape (2, posx, posy), float for inf sentinel
    lengths[:, origin[0], origin[1]] = 0
    for i,line in enumerate(inp.splitlines()):
        pos = origin.copy()
        pathlen = 0
        for word in line.split(','):
            dir,length = word[0], int(word[1:])
            l = np.arange(1, length + 1)
            # need min(...) for masking, hence inf sentinel
            if dir == 'R':
                lengths[i, pos[0] + l, pos[1] + 0*l] = np.minimum(l + pathlen, lengths[i, pos[0] + l, pos[1] + 0*l])
                pos += [length, 0]
            if dir == 'L':
                lengths[i, pos[0] - l, pos[1] + 0*l] = np.minimum(l + pathlen, lengths[i, pos[0] - l, pos[1] + 0*l])
                pos += [-length, 0]
            if dir == 'U':
                lengths[i, pos[0] + 0*l, pos[1] + l] = np.minimum(l + pathlen, lengths[i, pos[0] + 0*l, pos[1] + l])
                pos += [0, length]
            if dir == 'D':
                lengths[i, pos[0] + 0*l, pos[1] - l] = np.minimum(l + pathlen, lengths[i, pos[0] + 0*l, pos[1] - l])
                pos += [0, -length]
            pathlen += length

    # unmask, return int array of paths
    lengths[np.isinf(lengths)] = -1
    return lengths.astype(np.uint8)

def walk_lines(inp, origin, crosses):
    """Linear path length solver looking for crossings, returns every length"""

    crossset = set(zip(*crosses))
    crossdats = []  # keeps pos: length dict for each crossing, for each wire
    for i,line in enumerate(inp.splitlines()):
        pos = origin.copy()
        pathlen = 0
        crossdat = {}
        seens = set()
        for word in line.split(','):
            dir,length = word[0], int(word[1:])
            if dir == 'R':
                step = [1, 0]
            if dir == 'L':
                step = [-1, 0]
            if dir == 'U':
                step = [0, 1]
            if dir == 'D':
                step = [0, -1]
            for _ in range(length):
                pos += step
                pathlen += 1
                tpos = tuple(pos)
                if tpos in seens:
                    continue
                seens.add(tpos)
                if tpos in crossset:
                    crossdat[tpos] = pathlen
        crossdats.append(crossdat)
    keys = crossdats[0].keys()
    lengths = [[crossdat[k] for k in keys] for crossdat in crossdats]
    sums = [sum(ls) for ls in zip(*lengths)]
    return sums

def day03(inp):
    origin,wires = get_wires(inp)
    #print_wires(origin, wires)
    # wires is ~ 700 MB for real input

    # mask out origin, find crossings
    wires[:, origin[0], origin[1]] = False
    crosses = wires.all(0).nonzero()
    dists = abs(crosses[0] - origin[0]) + abs(crosses[1] - origin[1])
    closest = dists.argmin()
    part1 = dists[closest]

    # brute force solver: MemoryError due to floats
    #pathlengths = get_pathlengths(inp, origin, wires)  # array with shape (2, posx, posy)
    #crosslengths = pathlengths[:, crosses[0], crosses[1]]  # shape (2, ncross)
    #part2 = crosslengths.sum(0).min()

    # walk over each wire... safe
    crosslengths = walk_lines(inp, origin, crosses)
    part2 = min(crosslengths)

    return part1, part2


if __name__ == "__main__":
    testinp = open('day03.testinp').read()
    print(day03(testinp))
    inp = open('day03.inp').read()
    print(day03(inp))
