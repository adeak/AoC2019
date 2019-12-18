from collections import defaultdict
from itertools import count
from string import ascii_uppercase as caps
from string import ascii_lowercase as lowers

# # working but too slow/too much memory:
# def bfs_with_keys(board, pos0, num_keys):
#     # each pathinfo is a (list_of_poses, list_of_keys) tuple
#     # also keep track of visited positions with (pos, keys) sets
#     pathinfos = [([pos0], [])]
#     seens = {(pos0, frozenset())}
#     for step in count(1):
#         next_pathinfos = []
#         for poses,keys in pathinfos:
#             pos = poses[-1]
#             for dx,dy in [(1,0), (0,-1), (-1,0), (0,1)]:
#                 nextpos = pos[0] + dx, pos[1] + dy
#                 if (nextpos, frozenset(keys)) in seens:
#                     continue
# 
#                 c = board[nextpos]
#                 if c == '.' or (c in caps and c.lower() in keys) or (c in keys):
#                     # we can step but nothing else
#                     next_pathinfos.append((poses + [nextpos], keys.copy()))
#                     seens.add((nextpos, frozenset(keys)))
#                 elif c in lowers:
#                     # we've got a new key
#                     nextkeys = keys + [c]
#                     if len(nextkeys) == num_keys:
#                         # we've found a shortest path
#                         return step, nextkeys
#                     next_pathinfos.append((poses + [nextpos], nextkeys))
#                     seens.add((nextpos, frozenset(nextkeys)))
# 
#         pathinfos = next_pathinfos
        
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

def day18(inp):
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

    shortest = bfs_with_keys(board, start, num_keys)

    return shortest


if __name__ == "__main__":
    testinp = open('day18.testinp').read()
    print(day18(testinp))
    inp = open('day18.inp').read()
    print(day18(inp))
