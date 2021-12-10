import datetime as dt
import math
import random
import time
from collections import deque
import alles


def hour_and_minutes_to_velocity(hour, minutes, starting_hour, total_duration_minutes):
    current_minutes = ((hour - starting_hour) * 60) + minutes
    if current_minutes > total_duration_minutes:
        return 0
    old_range = total_duration_minutes
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


def get_durations(num_attacks, total_duration):
    r = [random.random() for i in range(5)]
    x = [n / sum(r) for n in r]
    return [int(n * total_duration) for n in x]


def get_start_times(durations):
    starts_and_durations = []
    for i, duration in enumerate(durations):
        if i == 0:
            starts_and_durations.append((0, duration))
        else:
            starts_and_durations.append((sum(durations[0:i]), duration))
    return starts_and_durations


def add_notes(starts_and_durations, note):
    return [(s_d[0], s_d[1], note) for s_d in starts_and_durations]


def play_note(osc_id, num_oscs, num_speakers, note, velocity, duration):
    first_breakpoint_ms = round(((duration) / 2) * 1000)
    second_breakpoint_ms = round((duration) * 1000)
    breakpoint_string = f"{first_breakpoint_ms},10,{second_breakpoint_ms},0.05,500,0"

    if note > 72:
        velocity = velocity / 2
    elif note > 60:
        velocity = velocity / 1.5
    print("sending ... ", osc_id, note, velocity, duration)
    alles.send(
        osc=osc_id,
        bp0=breakpoint_string,
        bp0_target=alles.TARGET_AMP,
        wave=alles.TRIANGLE,
        vel=velocity / 15,
        note=note,
        client=osc_id % num_speakers,
    )
    osc_id += 1
    next_osc_id = osc_id % num_oscs
    return next_osc_id


chords_of_the_week = {
    0: [5, 9, 0],  # f+
    1: [0, 4, 7],  # c+
    2: [7, 11, 2],  # g+
    3: [2, 6, 9],  # d+
    4: [9, 1, 4],  # a+
    5: [4, 8, 11],  # e+
}

start_hour = 7
end_hour = 8
total_duration_minutes = (end_hour - start_hour) * 60
octaves = [4, 5, 6]  # let's go 3 octaves
num_oscs = 12
num_speakers = 3
time_to_sleep = 300

while True:
    hour = dt.datetime.now().hour
    minutes = dt.datetime.now().minute
    weekday = dt.datetime.today().weekday()
    if hour < start_hour or hour >= end_hour or weekday >= 6:
        print(hour, start_hour, end_hour)
        print("nothing to do ...")
        time.sleep(time_to_sleep)
        continue
    alles.reset()  # just in case, before we start ...

    pitches = chords_of_the_week[weekday]
    velocity = hour_and_minutes_to_velocity(
        hour, minutes, start_hour, total_duration_minutes
    )
    print("time and velocity:  ", hour, minutes, velocity)

    next_voice = random.randint(60, 240)

    all_events = []
    notes = get_notes(octaves, pitches)
    for note in notes:
        num_attacks = random.randint(3, 10)
        durations = get_durations(num_attacks, next_voice)
        starts_and_durations = get_start_times(durations)
        times_and_note = add_notes(starts_and_durations, note)
        all_events.extend(times_and_note)
    # sort by start time
    sorted_events = sorted(all_events, key=lambda event: event[0])

    current_time = 0
    osc_id = 0
    for start, duration, note in sorted_events:
        if start <= current_time:
            # play our starting note(s)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note, velocity, duration)
        else:
            # sleep until the next start time, and then play it!
            time_to_current = start - current_time
            time.sleep(time_to_current)
            current_time += time_to_current
            osc_id = play_note(osc_id, num_oscs, num_speakers, note, velocity, duration)
