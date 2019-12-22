# part1
def day22(inp):
    num_cards = 10007
    target = 2019
    num_iters = 1

    # follow only the target's position

    # increment: position = (position*increment) % num_cards
    # new deck: position = num_cards - 1 - position
    # cut: position = (position - val) % num_cards

    # parse inputs once
    shuffling = []
    for line in inp.rstrip().splitlines():
        if line.startswith('deal with increment'):
            step = int(line.split()[-1])
            shuffling.append(lambda pos, step=step: (pos*step) % num_cards)
        elif line.startswith('deal into new'):
            shuffling.append(lambda pos: num_cards - 1 - pos)
        elif line.startswith('cut'):
            val = int(line.split()[-1])
            shuffling.append(lambda pos, val=val: (pos - val) % num_cards)
        else:
            assert False, f'Impossible case {line}!'

    pos_history = [target]
    seen_poses = {target}
    pos = target

    # shuffle once:
    for stepfun in shuffling:
        pos = stepfun(pos)

    return pos

# part 2: cheating (LCG from reddit, cracking LCG from -v, fast skipping from post linked below)
# cracking a linear congruential generator from https://tailcall.net/blog/cracking-randomness-lcgs/ via reddit
def crack_unknown_increment(states, modulus, multiplier):
    increment = (states[1] - states[0]*multiplier) % modulus
    return modulus, multiplier, increment
def crack_unknown_multiplier(states, modulus):
    multiplier = (states[2] - states[1]) * modinv(states[1] - states[0], modulus) % modulus
    return crack_unknown_increment(states, modulus, multiplier)
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)
def modinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n

def modpow(b, e, m):
    """Modular exponentiation according to https://en.wikipedia.org/wiki/Modular_exponentiation"""
    # using binary speed-up
    if e == 0:
        return b % m
    elif e > 0:
        res = b
        curr_exponent = 1
        exps = {curr_exponent: res}
        while curr_exponent <= e//2:
            res = (res**2) % m
            curr_exponent *= 2
            exps[curr_exponent] = res
        while curr_exponent < e:
            # find highest computed exponent
            highest = max(exp for exp in exps.keys() if exp <= e - curr_exponent)
            res = (res * exps[highest]) % m
            curr_exponent += highest
        return res
    else:
        d = modinv(b, m)
        return modpow(d, -e, m)

def day22b(inp):
    num_cards = 119315717514047
    target = 2020
    num_iters = 101741582076661
    # part 1 sanity check for the reversed algo:
    #num_cards = 10007
    #target = 1234
    #num_iters = 1

    # follow only the target's position

    # direct rules:
    # increment: position = (position*increment) % num_cards
    # new deck: position = num_cards - 1 - position
    # cut: position = (position - val) % num_cards
    #
    # BUT WE NEED THIS IN REVERSE!
    # increment: unique orig_pos for which (orig_pos*increment) % num_cards == pos
    # new deck: orig_pos = num_cards - 1 - pos
    # cut: orig_pos = (pos + val) % num_cards

    # create a lookup table to invert (orig_pos*increment) % num_cards == pos
    # this is equivalent to orig_pos = (n*max + pos)//step
    #     where n is such that (pos mod step) + n*(max mod step) is 0 mod step
    #     (max mod step) is fixed
    #     (pos mod step) can be at most step different values
    inc_lookup = {}  # step, posmod -> n
    for line in inp.rstrip().splitlines():
        if 'increment' not in line:
            continue
        step = int(line.split()[-1])
        maxmod = num_cards % step
        for posmod in range(step):
            n = next(n for n in range(step) if not (posmod + n*maxmod) % step)
            inc_lookup[step, posmod] = n

    # now build a single function call for a shuffling cycle
    # don't use sympy: lambdify turns pos//n into floor(pos/n) which forces floats...

    body = ['def shuffle_fun(pos):']

    # parse inputs once backwards
    for line in reversed(inp.rstrip().splitlines()):
        if line.startswith('deal with increment'):
            step = int(line.split()[-1])
            body.append(f'pos = (inc_lookup[{step}, pos % {step}]*{num_cards} + pos)//{step}')
        elif line.startswith('deal into new'):
            body.append(f'pos = {num_cards - 1} - pos')
        elif line.startswith('cut'):
            val = int(line.split()[-1])
            body.append(f'pos = (pos + {val}) % {num_cards}')
        else:
            assert False, f'Impossible case {line}!'
    body.append('return pos')
    namespace = {'inc_lookup': inc_lookup}
    exec('\n    '.join(body), namespace)
    shuffle_fun = namespace['shuffle_fun']

    # if we actually did the simulations this would be pretty fast: only 111 years needed given memory for the history

    pos_history = [target]
    pos = target
    for shuffle_iter in range(num_iters):
        # shuffle once:
        pos = shuffle_fun(pos)

        pos_history.append(pos)

        if len(pos_history) == 3:
            # try breaking the LCG, modulus is num_cards
            _, multiplier, increment = crack_unknown_multiplier(pos_history[::-1], num_cards)
            break

    # now step shuffle_iter steps backward with the LCG
    # use https://www.nayuki.io/page/fast-skipping-in-a-linear-congruential-generator for fast skipping backwards
    mod = num_cards
    a = multiplier
    b = increment
    a_prime = modinv(a, mod)
    b_prime = (-modinv(a, mod) * b) % mod
    first_term = (modpow(a_prime, num_iters, mod) * target) % mod
    numerator = (modpow(a_prime, num_iters, (a_prime - 1)*mod) - 1) % ((a_prime - 1)*mod)
    denominator = (a_prime - 1)
    second_term = (numerator // denominator * b_prime) % mod
    start = (first_term + second_term) % mod

    # check that we got it right (fast skip back forward)
    first_term = (modpow(a, num_iters, mod) * start) % mod
    second_term = ((modpow(a, num_iters, (a - 1)*mod) - 1) % ((a - 1)*mod) // (a - 1) * b) % mod
    assert target == (first_term + second_term) % mod

    return start

if __name__ == "__main__":
    inp = open('day22.inp').read()
    print(day22(inp))
    print(day22b(inp))
