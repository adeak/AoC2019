import numpy as np

def fuel_from_mass(m):
    """Compute a single iteration of mass -> fuel assuming numpy input"""
    return (m/3).astype(int) - 2

def day01(inp):
    ms = np.fromstring(inp, sep=' ')

    fuels = fuel_from_mass(ms)
    part1 =  fuels.sum()

    tot_fuel = 0
    for m in ms:
        mtmp = m
        while True:
            fuel = fuel_from_mass(mtmp)
            if fuel <= 0:
                break
            tot_fuel += fuel
            mtmp = fuel
    part2 = tot_fuel

    return part1, part2


if __name__ == "__main__":
    inp = open('day01.inp').read()
    print(day01(inp))
