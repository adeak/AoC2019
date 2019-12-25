from intcode import Intcode

def simulate(src):
    comp = Intcode(src)

    dirs = {'n': 'north', 'e': 'east', 's': 'south', 'w': 'west', 'i': 'inv'}
    
    last_output_len = 0
    while True:
        if comp.next_op == 'in':
            new_outputs = comp.outputs[last_output_len:]
            last_output_len = len(comp.outputs)
            # print console
            print(bytes(new_outputs).decode('ascii'))

            while True:
                # get a choice: north/east/south/west | take <thing> | drop <thing> | inv
                # the single-word commands only need the first letter
                choice = input()
                choice = choice.lower()
                if choice.startswith('q'):
                    print('Quitting simulation...')
                    return ''
                if choice.startswith(tuple('nsewi')):
                    choice = dirs[choice[0]]
                    break
                if choice.split()[0] not in ['take', 'drop']:
                    print('Invalid input!')
                    continue
                break

            next_inp = f'{choice}\n'.encode('ascii')
            comp.inputs.extend(next_inp)
            
            # now step over the corresponding input instructions
            read_count = 0
            while True:
                comp.step()
                if comp.last_op == 'in':
                    read_count += 1

                if read_count == len(next_inp):
                    break

        comp.step()

        if comp.last_op is None:
            return bytes(comp.outputs[last_output_len:]).decode('ascii')

def day25(inp):
    src = list(map(int, inp.strip().split(',')))

    pwd = simulate(src)

    return pwd

if __name__ == "__main__":
    inp = open('day25.inp').read()
    print(day25(inp))
    # strategy: first find the necessary heaviest (boulder),
    #           exclude the second heaviest (mutex),
    #           exclude each of the remaining six items one at a time
    #           classify them into 3 light + 3 heavy
    #           keep necessary heaviest and lightest three
