from operator import itemgetter
from collections import defaultdict
from itertools import count
from string import ascii_uppercase as caps

def parse_inputs(inp):
    tmp_board = {}
    for j,line in enumerate(inp.rstrip().splitlines()):
        for i,c in enumerate(line):
            if c not in '#.' + caps:
                continue
            tmp_board[i,j] = c  # step left is [1,0], down step is [0,1]

    # filter out fluff
    board = {pos:val for pos,val in tmp_board.items() if val in '#.'}

    # find portals
    portal_coords = defaultdict(list)
    board_portalupdate = {}
    for pos,c in board.items():
        # check edges of the board for portals and end/start
        if c == '#':
            continue

        i,j = pos

        if tmp_board[i - 1, j] in caps:
            # either a portal or start
            label = ''.join([tmp_board[i - 2, j], tmp_board[i - 1, j]])
            portalpos = i - 1, j
        elif tmp_board[i + 1, j] in caps:
            label = ''.join([tmp_board[i + 1, j], tmp_board[i + 2, j]])
            portalpos = i + 1, j
        elif tmp_board[i, j - 1] in caps:
            label = ''.join([tmp_board[i, j - 2], tmp_board[i, j - 1]])
            portalpos = i, j - 1
        elif tmp_board[i, j + 1] in caps:
            label = ''.join([tmp_board[i, j + 1], tmp_board[i, j + 2]])
            portalpos = i, j + 1
        else:
            continue

        if label == 'AA':
            start = pos
        elif label == 'ZZ':
            target = pos
        else:
            portal_coords[label].append(pos)
            board_portalupdate[portalpos] = 'P'  # signal portal for neighbour search later
    board.update(board_portalupdate)

    # turn the portal_coords into a bijective mapping
    portals = {}
    for pos1,pos2 in portal_coords.values():
        portals[pos1] = pos2
        portals[pos2] = pos1

    return board,portals,start,target

def bfs(board, portals, start, target, with_levels=False):
    # find extremal coordinates for "outer" vs "inner" positions, with correction for portal positions
    x_edges = [min(board.keys(), key=itemgetter(0))[0] + 1, max(board.keys(), key=itemgetter(0))[0] - 1]
    y_edges = [min(board.keys(), key=itemgetter(1))[1] + 1, max(board.keys(), key=itemgetter(1))[1] - 1]

    # hacky part 1 vs part 2: don't shift levels for part 1 (and watch portals on the edge)
    level_shift = 1 if with_levels else 0

    pos = start
    edges = {(0, pos)}  # (level, position)
    seens = {(0, pos)}
    # hack: avoid AA vacuum
    for neighb in [(pos[0], pos[1] - 1), (pos[0], pos[1] + 1), (pos[0] - 1, pos[1]), (pos[0] + 1, pos[1])]:
        if neighb not in board:
            # then this is the "AA" label which we have to skip
            seens.add((0, neighb))

    for step in count(1):
        next_edges = set()
        for level,pos in edges:
            for dx,dy in [(1,0), (0,-1), (-1,0), (0,1)]:
                nextlevel = level
                nextpos = pos[0] + dx, pos[1] + dy
                if (level,nextpos) in seens or board[nextpos] == '#':
                    continue
                if board[nextpos] == 'P':
                    # we might have to go through the corresponding portal
                    if with_levels and level == 0 and (pos[0] in x_edges or pos[1] in y_edges):
                        # then this is actually a wall
                        continue
                    # else we have a portal, decide direction
                    if pos[0] in x_edges or pos[1] in y_edges:
                        # outer ring
                        nextlevel -= level_shift
                    else:
                        # inner ring
                        nextlevel += level_shift
                    nextpos = portals[pos]
                if nextpos == target:
                    # we may be done
                    if not with_levels or level == 0:
                        # we're done
                        return step
                    # else this is a wall
                    continue
                if nextpos == start:
                    # we never want to come back to this dead end anyway
                    continue

                next_edges.add((nextlevel, nextpos))
                seens.add((nextlevel, nextpos))
        edges = next_edges

def day20(inp):
    board,portals,start,target = parse_inputs(inp)

    part1 = bfs(board, portals, start, target)
    part2 = bfs(board, portals, start, target, with_levels=True)

    return part1,part2

if __name__ == "__main__":
    testinp = open('day20.testinp').read()
    print(day20(testinp))
    inp = open('day20.inp').read()
    print(day20(inp))
