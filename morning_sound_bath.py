import datetime as dt
import math
import random
import time

import alles


def hour_and_minutes_to_velocity(hour, minutes, starting_hour, duration):
    current_minutes = (hour - starting_hour * 60) + minutes
    if current_minutes > duration:
        return 0
    old_range = duration  # in minutes
    new_range = math.pi
    sine_value = math.sin((((current_minutes - 0) * new_range) / old_range) + 0)
    return sine_value


def get_notes(octaves, pitches):
    notes = []
    for pitch in pitches:
        note = (random.choice(octaves) * 12) + pitch
        print(pitch, note)
        notes.append(note)
    return notes


# let's go 3 octaves
# C, E, G, B
octaves = [4, 5, 6]
pitches = [0, 4, 7, 11]
num_speakers = 3

while True:
    hour = dt.datetime.now().hour
    minutes = dt.datetime.now().minute
    velocity = hour_and_minutes_to_velocity(hour, minutes, 16, 120)
    print(hour, minutes, velocity)

    next_sleep = random.randint(60, 240)
    first_breakpoint_ms = round(((next_sleep - 1) / 2) * 1000)
    second_breakpoint_ms = round((next_sleep - 1) * 1000)
    breakpoint_string = f"{first_breakpoint_ms},10,{second_breakpoint_ms},0.05,500,0"

    osc_id = 0
    notes = get_notes(octaves, pitches)
    for note in notes:
        if random.random() > 0.25:
            alles.send(
                osc=osc_id,
                bp0=breakpoint_string,
                bp0_target=alles.TARGET_AMP,
                wave=alles.SINE,
                vel=velocity / 10,
                note=note,
                client=osc_id % num_speakers,
            )
            print("sending ... ", osc_id, note, velocity)
            osc_id = osc_id + 1
    time.sleep(next_sleep)
