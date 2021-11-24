import datetime
import math
import random


def hour_and_minutes_to_velocity(hour, minutes, starting_hour, duration):
    current_minutes = (hour - starting_hour * 60) + minutes
    if current_minutes > duration:
        return 0
    old_range = duration  # in minutes
    new_range = math.pi
    sine_value = math.sin((((total_minutes - 0) * new_range) / old_range) + 0)
    return 55 * sine_value + 5


def get_notes(octaves, pitches, velocity):
    notes = []
    for pitch in pitches:
        note = (random.choice(octaves) * 12) + pitch
        notes.append(note)
    num_notes = math.min(((velocity / 15) + randoml.randint(1, 2)), 4)
    while len(notes) > num_notes:
        i = random.randint(0, len(test) - 1)
        del notes[i]
    return notes


# let's go 4 octaves, from 48 to 96
octaves = [4, 5, 6, 7]
pitches = [0, 4, 7, 11]  # C, E, G, B, these will change daily


while true:
    hour = dt.datetime.now().hour
    minutes = dt.datime.now().minute
    velocity = hour_and_minutes_to_velocity(hour, minutes, 6, 120)

    osc_id = 0
    notes = get_notes(octaves, pitches, velocity)
    for note in notes:
        if random.random() > 0.5:
            alles.send(
                osc=osc_id,
                wave=alles.SQUARE,
                filter_freq=5000,
                resonance=5,
                filter_type=alles.FILTER_LPF,
            )
            alles.send(osc=osc_id, vel=velocity, note=note)
            osc_id = (osc_id + 1) % 3
    next_sleep = random.randint(30, 240)
    sleep(next_sleep)
