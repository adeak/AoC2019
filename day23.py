from collections import deque
from intcode import Intcode

# coroutine-ify the processes: yield on input and output
def proc_coro(comp, addr, msgs):
    last_len = 0  # last output stream length
    
    # initialize with address
    comp.inputs.append(addr)

    while True:
        if comp.next_op is None:
            break

        if comp.next_op == 'in' and not comp.inputs:
            # load inputs from msg queue, clear queue
            if not msgs:
                msgs.append(-1)
            comp.inputs.extend(msgs)
            msgs.clear()

            yield 

        if comp.last_op == 'out' and len(comp.outputs) == last_len + 3:
            # then we have a new output triple
            yield comp.outputs[-3:]
            last_len = len(comp.outputs)

        comp.step()

def simulate(src, num_procs=50):
    comps = {addr: Intcode(src) for addr in range(num_procs)}
    coros = {}
    msgs = {}
    for addr,comp in comps.items():
        # initialize coroutines with address and message queue
        msgs[addr] = []
        coro = proc_coro(comp, addr, msgs[addr])
        coros[addr] = coro
        coro.send(None)

    last_buffer = None  # for part 2
    last_sent = None  # for part 2
    halteds = set()
    have_msgs = deque([True, True], maxlen=2)  # check if there were new msgs during iteration in two successive passes
    while True:
        have_msgs_now = False
        for addr,coro in coros.items():
            try:
                # step with the coro
                retval = next(coro)
            except StopIteration:
                # this process stopped (not really relevant)
                halteds.add(addr)
            else:
                if retval is not None:
                    # then we have output
                    to, *xy = retval

                    if to in coros:
                        # send it to the process
                        msgs[to].extend(xy)
                        have_msgs_now = True
                    elif to == 255:
                        # send it to the buffer
                        if not last_buffer:
                            # part 1: first NAT buffer value
                            part1 = xy[-1]
                        last_buffer = xy

        # check if we had any new messages
        have_msgs.append(have_msgs_now)

        # filter out finished processes, if any
        coros = {addr: coro for addr,coro in coros.items() if addr not in halteds}
        if not coros:
            break

        # check for part 2
        # heuristic: check lack of new messages in 2 successive passes
        if not any(have_msgs):
            x,y = xy = last_buffer
            if y == last_sent:
                # part 2 done too
                part2 = y
                return part1, part2

            # otherwise reset the network
            msgs[0].extend(xy)
            have_msgs.append(True)
            last_sent = y

def day23(inp):
    src = list(map(int, inp.strip().split(',')))

    part1,part2 = simulate(src)

    return part1,part2

if __name__ == "__main__":
    inp = open('day23.inp').read()
    print(day23(inp))
