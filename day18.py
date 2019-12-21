from collections import defaultdict
from itertools import count, product
from string import ascii_uppercase as caps
from string import ascii_lowercase as lowers
import numpy as np  # only for printing

class Node:
    def __init__(self, label=''):
        self.label = label
        self.children = []

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

def find_dependencies(board, start):
    pos = start
    seens = set(start)
    paths = [(start, [])]  # (edge_pos, history_list) tuples
    final_paths = []
    key_steps = {}  # letter -> steps
    for steps in count(1):
        next_paths = []
        for pos,history in paths:
            path_count = len(next_paths)
            for dx,dy in [(1,0), (0,-1), (-1,0), (0,1)]:
                nextpos = pos[0] + dx, pos[1] + dy
                if nextpos in seens:
                    continue

                c = board[nextpos]
                if c == '#':
                    # wall
                    continue
                if c in caps + lowers:
                    history_now = history + [c]
                    if c in lowers:
                        key_steps[c] = steps
                else:
                    history_now = history.copy()
                next_paths.append((nextpos, history_now))
                seens.add(nextpos)

            if len(next_paths) <= path_count:
                # then this path terminated, remember it unless it's a dead end or already seen
                if history and history not in final_paths:
                    # also strip off dangling doors at the end
                    final_paths.append(''.join(history).rstrip(caps))

        paths = next_paths

        if not paths:
            # we're done
            break

    # parse dependencies into a tree for this quadrant
    root = Node('@')
    for history in final_paths:
        parent = root
        for c in history:
            current = next((child for child in parent.children if child.label == c), None)
            if current:
                # step down into the tree
                parent = current
                continue
            # otherwise new child
            current = Node(c)
            parent.children.append(current)
            parent = current

    return root, key_steps

def bfs_to_target(board, start, target, keys):
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
                elif c == '.' or (c in caps and c.lower() in keys) or (c in lowers):
                    # just step, ignore decoration
                    next_edges.add(nextpos)
                    seens.add(nextpos)
                    continue
                # else we have a closed door -> ignore for now
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

    # part 2: first build a dependency graph for each quadrant
    poses = {'TL': (start[0] - 1, start[1] - 1),
             'TR': (start[0] - 1, start[1] + 1),
             'BL': (start[0] + 1, start[1] - 1),
             'BR': (start[0] + 1, start[1] + 1)
             }

    dependencies = {quadrant: find_dependencies(board, start) for quadrant,start in poses.items()}
    # find_dependencies returns root nodes in a tree and a dict of steps needed for keys

    all_keysteps = {}  # letter -> steps
    for _,keysteps in dependencies.values():
        all_keysteps.update(keysteps)
    all_edges = {node: quadrant for quadrant,(root,_) in dependencies.items() for node in root.children}

    # do BFS-like thing
    # heuristic: always target the key that's closest to the respective starting point
    #            but try to go for keys in dead ends first
    keys = set()
    commands = []  # (quadrant, key) pairs
    for quadrant_steps in count(1):
        # find the nearest key
        keys_compare = set()
        for edge,quadrant in all_edges.items():
            c = edge.label
            if c in lowers:
                # penalize non-dead-ends and hope for the best
                dead_end_hack = 1000 if edge.children else 0
                keys_compare.add((all_keysteps[c] + dead_end_hack, quadrant, c))
        _,quadrant,k = min(keys_compare)
        commands.append((quadrant, k))
        keys.add(k)

        if len(keys) == num_keys:
            # we're done building up the commands
            break

        # find the new edges with the newest key, stop at closed doors or keys
        while True:
            dropped_edges = set()
            next_all_edges = {}
            for edge,quadrant in all_edges.items():
                c = edge.label
                if (c in caps and c.lower() in keys) or c in keys:
                    # we can ignore this door or used key from now
                    dropped_edges.add(edge)
                    next_all_edges.update((child,quadrant) for child in edge.children)
                else:
                    # keep this door or key
                    next_all_edges[edge] = quadrant
            if not dropped_edges:
                # then nothing happened in the last iteration, we're done
                break
            all_edges = next_all_edges

    # now do coordinated bfs according to each command, count the steps
    tot_steps = 0
    keys = set()
    for quadrant, target in commands:
        steps,pos = bfs_to_target(board, poses[quadrant], target, keys)
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
