import datetime as dt
import math
import random
import time

import alles


def hour_and_minutes_to_velocity(hour, minutes, starting_hour, duration):
    current_minutes = ((hour - starting_hour) * 60) + minutes
    if current_minutes > duration:
        return 0
    old_range = duration  # in minutes
    new_range = math.pi
    zero_to_pi = (((current_minutes - 0) * new_range) / old_range) + 0
    sine_value = math.sin(zero_to_pi)
    return sine_value


def get_notes(octaves, pitches):
    notes = []
    for pitch in pitches:
        note = (random.choice(octaves) * 12) + pitch
        notes.append(note)
    return notes


# let's go 3 octaves
# C, E, G, will need to automate my chords
start_hour = 7
duration = 120
end_hour = 9

octaves = [4, 5, 6]
pitches = [0, 4, 7]

num_speakers = 3

while True:
    hour = dt.datetime.now().hour
    minutes = dt.datetime.now().minute
    if hour < start_hour or hour > end_hour:
        print(hour, start_hour, end_hour)
        print("nothing to do yet ...")
        time.sleep(300)
        continue
    velocity = hour_and_minutes_to_velocity(hour, minutes, start_hour, duration)
    print(hour, minutes, velocity)

    next_sleep = random.randint(60, 240)
    first_breakpoint_ms = round(((next_sleep - 1) / 2) * 1000)
    second_breakpoint_ms = round((next_sleep - 1) * 1000)
    breakpoint_string = f"{first_breakpoint_ms},10,{second_breakpoint_ms},0.05,500,0"

    osc_id = 0
    notes = get_notes(octaves, pitches)
    for note in notes:
        if note > 72:
            velocity = velocity / 2
        elif note > 60:
            velocity = velocity / 1.5
        alles.send(
            osc=osc_id,
            bp0=breakpoint_string,
            bp0_target=alles.TARGET_AMP,
            wave=alles.TRIANGLE,
            vel=velocity / 10,
            note=note,
            client=osc_id % num_speakers,
        )
        print("sending ... ", osc_id, note, velocity)
        osc_id = osc_id + 1
    time.sleep(next_sleep)
