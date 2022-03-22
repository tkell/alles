def make_just_roots(starting_hz):
    octave = starting_hz * 2
    roots = []
    for i in range(0, 7):
        if i == 0:
            root = starting_hz
        else:
            root = starting_hz * ((3 / 2) ** i)

        while root > octave:
            root = root / 2
        roots.append(root)
    return roots


def make_just_intonation_chords(root):
    third = root * (5 / 4)
    fifth = root * (3 / 2)
    return [root, third, fifth]
