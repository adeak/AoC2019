from collections import defaultdict
from itertools import count,product
from string import ascii_uppercase as caps
from string import ascii_lowercase as lowers
import numpy as np  # only for printing

def bfs_with_keys(board, pos0, num_keys):
    # keep track of the "seen key sets" at a given position,
    # use propagators starting at keys to spread keys,
    # each propagator has its set of keys,
    # stop if we have all the keys
    seens = defaultdict(set)
    seens[pos0].add(frozenset())
    propagator_edges = {}
    propagator_edges[frozenset()] = {pos0}
    for step in count(1):
        next_propagators = {}
        for propkeys,edges in propagator_edges.items():
            next_edges = set()
            for pos in edges:
                for dx,dy in [(1,0), (0,-1), (-1,0), (0,1)]:
                    nextpos = pos[0] + dx, pos[1] + dy
                    if propkeys in seens[nextpos]:
                        # we've already been there or better
                        continue
    
                    c = board[nextpos]
                    if c == '#':
                        # wall
                        continue
                    elif c in caps and c.lower() not in propkeys:
                        # we can't open it (yet)
                        continue
                    elif c in caps or c == '.':
                        # we can step but that's all
                        seens[nextpos].add(propkeys)
                        next_edges.add(nextpos)
                    elif c in lowers:
                        # we might have found a new key
                        if c not in propkeys:
                            # new key: spawn new, expanded propagator,
                            #          or update existing one
                            next_keys = propkeys | frozenset(c)
                            if len(next_keys) == num_keys:
                                # we've found a shortest path
                                return step
                            next_prop_edges = {nextpos} | next_propagators.get(next_keys, frozenset())
                            next_propagators[next_keys] = next_prop_edges
                            seens[nextpos].add(next_keys)
                            # but don't add to next_edges!
                        else:
                            # we already have this key, just step over it
                            seens[nextpos].add(propkeys)
                            next_edges.add(nextpos)
                    else:
                        assert False, f'Impossible character {c} in step {step}'
            if next_edges:
                # keep this propagator
                next_propagators[propkeys] = next_edges
        propagator_edges = next_propagators
        if not propagator_edges:
            # this should never happen
            assert False, "We've never found all the keys..."

def bfs_to_target(board, start, target, keys, ignore_doors):
    """Walk on the board from a given starting point until target, given keys"""
    seens = set()
    pos = start
    edges = {pos}
    for steps in count(1):
        next_edges = set()
        for pos in edges:
            for dx,dy in [(1,0), (0,-1), (-1,0), (0,1)]:
                nextpos = pos[0] + dx, pos[1] + dy
                if nextpos in seens:
                    continue

                c = board[nextpos]
                if c == target:
                    keys.add(target)
                    return steps, nextpos
                if c == '#':
                    # wall
                    continue
                elif c == '.' or (c in caps and c.lower() in keys) or (c in ignore_doors) or (c in lowers):
                    # just step, ignore decoration
                    next_edges.add(nextpos)
                    seens.add(nextpos)
                    continue
                elif c in caps:
                    assert False, f'Unexpected door {c} from {start}, only have keys {keys}!'
                else:
                    assert False, f'Impossible case {c}!'
        edges = next_edges

        if not edges:
            # should not happen
            break

    assert False, f'Ran out of maze looking for target {target} starting from {start}!'


def print_board(board):
    points = np.array(list(board.keys()))
    size = points.ptp(0) + 1
    mins = points.min(0)
    pixels = np.full(size, fill_value=' ', dtype='U1')
    pixels[tuple((points - mins).T)] = list(board.values())
    print('\n'.join([''.join([c for c in row]) for row in pixels.astype(str)]))
    print()

def day18(inp, no_part2=False):
    board = {}
    num_keys = 0
    for row,line in enumerate(inp.strip().splitlines()):
        for column,c in enumerate(line):
            if c == '@':
                start = row,column
                c = '.'
            board[row,column] = c
            
            if c in lowers:
                num_keys += 1
    # "up" is [0,-1] direction

    # part 1
    part1 = bfs_with_keys(board, start, num_keys)

    # part 2 reconfiguration
    for x,y in product(range(start[0] - 1, start[0] + 2), range(start[1] - 1, start[1] + 2)):
        if abs(x - start[0]) == abs(y - start[1]) == 1:
            board[x,y] = '.'  # these would be @
        else:
            board[x,y] = '#'

    #print_board(board)

    if no_part2:
        # part1 test input
        return part1, None

    # manual part 2 for now
    targetses = [
            ('TR', 'zlgat'),
            ('TL', 'ho'),
            ('BR', 'sx'),
            ('BL', 'pv'),
            ('TL', 'md'),
            ('BL', 'yq'),
            ('TR', 'rw'),
            ('BL', 'k'),
            ('BR', 'ic'),
            ('TL', 'e'),
            ('TR', 'bnufj'),
            ]
    ignore_doors = 'SLXJIRGM'

    poses = {'TL': (start[0] - 1, start[1] - 1),
             'TR': (start[0] - 1, start[1] + 1),
             'BL': (start[0] + 1, start[1] - 1),
             'BR': (start[0] + 1, start[1] + 1)
             }

    tot_steps = 0
    keys = set()
    for quadrant, targets in targetses:
        for target in targets:
            steps,pos = bfs_to_target(board, poses[quadrant], target, keys, ignore_doors)
            tot_steps += steps
            poses[quadrant] = pos
    assert len(keys) == num_keys
    part2 = tot_steps

    return part1, part2


if __name__ == "__main__":
    testinp = open('day18.testinp').read()
    print(day18(testinp, no_part2=True))
    inp = open('day18.inp').read()
    print(day18(inp))
