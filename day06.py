class Planet:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.totorbits = 0

    def adopt(self, child):
        self.children.append(child)
        child.parent = self

    def inherit_orbits(self):
        self.totorbits = self.parent.totorbits + 1


def day06(inp):
    orbs = {child: parent for parent, child in [row.split(')') for row in inp.strip().splitlines()]}
    planets = {child: Planet(child) for child in orbs}  # COM is missing, no parent
    planets['COM'] = Planet('COM')

    for child,parent in orbs.items():
        planets[parent].adopt(planets[child]) 

    root = planets['COM']

    # walk the tree, count accumulated orbits, need BFS for counts
    bigtotal = 0
    stack = [root]
    next_stack = []
    while True:
        if not stack:
            # advance to next level
            stack = next_stack
            next_stack = []
        if not stack:
            # we're all done
            break

        nxt = stack.pop(-1)

        for child in nxt.children:
            child.inherit_orbits()
            bigtotal += child.totorbits

            if child.children:
                next_stack.append(child)

            # for part 2
            if child.name == 'YOU':
                me = child

    part1 = bigtotal

    # now do BFS from YOU
    dist = 1
    stack = [me]
    next_stack = []
    seens = set()
    while True:
        if not stack:
            # advance to next level
            stack = next_stack
            next_stack = []
            dist += 1
        if not stack:
            # we're all done
            break
        nxt = stack.pop(-1)

        if nxt in seens:
            continue
        seens.add(nxt)

        if nxt.name == 'SAN':
            break

        for child in nxt.children + [nxt.parent]:
            if not child or child in seens:
                continue
            next_stack.append(child)

    part2 = dist - 3

    return part1, part2


if __name__ == "__main__":
    testinp = open('day06.testinp').read()
    print(day06(testinp))
    inp = open('day06.inp').read()
    print(day06(inp))
