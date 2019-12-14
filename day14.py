from collections import defaultdict
from itertools import count

def get_ore_need(reqs, fuel_need=1):
    needed = {'FUEL': fuel_need}
    leftovers = defaultdict(int)
    while needed.keys() != {'ORE'}:
        needed_next = defaultdict(int)
        for target,count in needed.items():
            if target == 'ORE':
                needed_next['ORE'] += count
                continue
            ntarget,req = reqs[target]
            # we need count units, we can produce ntarget at a time
            multi = -(-count // ntarget)  # ceildiv
            leftovers[target] += multi * ntarget - count
            for namesource,nsource in req.items():
                needed_next[namesource] += nsource * multi

        # subtract leftovers
        for leftname, leftcount in leftovers.items():
            used_up = min(leftcount, needed_next[leftname])
            needed_next[leftname] -= used_up
            leftovers[leftname] -= used_up
        needed.clear()
        needed.update((key,val) for key,val in needed_next.items() if val)

    return needed['ORE']

def day14(inp):
    reqs = {}
    for line in inp.strip().splitlines():
        fr,to = line.split(' => ')
        nto,nameto = to.split()
        comps = {name: int(n) for segment in fr.split(', ') for n,name in [segment.split()]}
        reqs[nameto] = (int(nto), comps)

    # reqs: result name -> (produced units, component dict)
    #   component dict: component name -> needed units

    min_ore_need = get_ore_need(reqs)
    part1 = min_ore_need

    have_ore = 1000000000000

    # bisection method for fuel capacity
    fuel_from = fuel_to = have_ore // min_ore_need
    # guaranteed to have enough ore here

    while True:
        if fuel_to - fuel_from == 1:
            # we're done
            part2 = fuel_from
            break

        if fuel_from == fuel_to:
            # stepping at the start, keep going
            fuel_amount = int(1.1 * fuel_to)
        else:
            # actual bisection
            fuel_amount = (fuel_from + fuel_to) // 2

        ore_need = get_ore_need(reqs, fuel_amount)
        #print(fuel_amount, ore_need)
        if ore_need > have_ore:
            # need to search to the left
            fuel_to = fuel_amount
        elif fuel_to == fuel_from:
            # need to step to the right at the start
            fuel_from = fuel_to = fuel_amount
        else:
            # need to step right during bisection
            fuel_from = fuel_amount

    return part1,part2


if __name__ == "__main__":
    testinp = open('day14.testinp').read()
    print(day14(testinp))
    inp = open('day14.inp').read()
    print(day14(inp))
