from collections import Counter

def check_pass(num):
    s = str(num)

    if s != ''.join(sorted(s)):
        # not sorted
        return False

    if len(set(s)) == len(s):
        # no repetitions
        return False

    return True

def check_pass_part2(num):
    s = str(num)

    if s != ''.join(sorted(s)):
        # not sorted
        return False

    # count repeating digits to make sure there's just-a-pair
    return 2 in Counter(s).values()

def day04(inp):
    first,second = map(int, inp.strip().split('-'))
    nums = range(first, second + 1)

    part1 = sum(map(check_pass, nums))
    part2 = sum(map(check_pass_part2, nums))
    return part1, part2

if __name__ == "__main__":
    inp = open('day04.inp').read()
    print(day04(inp))
