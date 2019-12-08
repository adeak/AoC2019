import numpy as np

def print_message(img):
    dat = img == 1
    print('\n'.join([''.join(['*' if c else ' ' for c in row]) for row in dat]))

def day08(inp, size=(25, 6)):
    dat = np.array([int(c) for c in inp.strip()]).reshape(-1, size[1], size[0])

    lay = (dat == 0).sum((1,2)).argmin()
    part1 = (dat[lay, ...] == 1).sum() * (dat[lay, ...] == 2).sum()

    img = np.full(dat.shape[1:], fill_value=-1)
    for lay in range(dat.shape[0]):
        inds = (img == -1) & (dat[lay, ...] != 2)
        img[inds] = dat[lay, inds]
    assert img[img == -1].sum() == 0, 'Transparent pixels left!'

    print_message(img)

    return part1

if __name__ == "__main__":
    testinp = open('day08.testinp').read()
    print(day08(testinp, size=(3, 2)))
    inp = open('day08.inp').read()
    print(day08(inp))
