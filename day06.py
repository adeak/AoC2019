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
        if self.parent:
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

        planet = stack.pop()
        planet.inherit_orbits()
        bigtotal += planet.totorbits

        if planet.name == 'YOU':
            me = planet

        if planet.children:
            next_stack.extend(planet.children)


    part1 = bigtotal

    # now do BFS from YOU
    dist = 0
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
        planet = stack.pop()

        if planet in seens:
            continue
        seens.add(planet)

        if planet.name == 'SAN':
            break

        if planet.parent:
            next_stack.append(planet.parent)
        if planet.children:
            next_stack.extend(planet.children)

    part2 = dist - 2

    return part1, part2


if __name__ == "__main__":
    testinp = open('day06.testinp').read()
    print(day06(testinp))
    inp = open('day06.inp').read()
    print(day06(inp))
