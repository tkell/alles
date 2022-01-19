import argparse
import datetime as dt

import math
import random
import time
from collections import deque
import alles


class Note:
    def __init__(self, frequency, velocity, volume, duration):
        self.frequency = frequency
        self.velocity = velocity
        self.volume = volume
        self.duration = duration

    def __repr__(self):
        return f"<Note: {self.frequency} hz, {self.velocity} velocity>"


def elapsed_time_to_velocity(current_time, start_time, total_duration_minutes):
    time_elapsed = current_time - start_time
    current_seconds = time_elapsed.seconds
    total_duration_seconds = total_duration_minutes * 60
    if current_seconds > total_duration_seconds:
        return 0
    old_range = total_duration_seconds
    new_range = math.pi
    zero_to_pi = (((current_seconds - 0) * new_range) / old_range) + 0
    sine_value = math.sin(zero_to_pi)
    return sine_value


def get_frequencies(octaves, frequencies):
    final_hz = []
    for frequency in frequencies:
        hz = frequency * (random.choice(octaves))
        final_hz.append(hz)
    return final_hz


def get_durations(num_attacks, total_duration):
    r = [random.random() for i in range(5)]
    x = [n / sum(r) for n in r]
    return [int(n * total_duration) for n in x]


def get_start_times(durations, start_offset):
    starts_and_durations = []
    for i, duration in enumerate(durations):
        if i == 0:
            starts_and_durations.append((0 + start_offset, duration))
        else:
            starts_and_durations.append((sum(durations[0:i]) + start_offset, duration))
    return starts_and_durations


def add_notes(starts_and_durations, hz):
    return [(s_d[0], s_d[1], hz) for s_d in starts_and_durations]


def play_note(osc_id, num_oscs, num_speakers, note):
    first_breakpoint_ms = round(((note.duration) / 2) * 1000)
    second_breakpoint_ms = round((note.duration) * 1000)
    breakpoint_string = f"{first_breakpoint_ms},10,{second_breakpoint_ms},0.05,500,0"

    print("sending ...", note, osc_id)
    alles.send(
        vel=note.velocity,
        volume=note.volume,
        freq=note.frequency,
        bp0=breakpoint_string,
        bp0_target=alles.TARGET_AMP,
        wave=alles.TRIANGLE,
        osc=osc_id,
        client=osc_id % num_speakers,
    )
    osc_id += 1
    next_osc_id = osc_id % num_oscs
    return next_osc_id


def make_just_intonation_chords(starting_hz):
    frequencies = {}
    octave = starting_hz * 2
    for i in range(0, 7):
        if i == 0:
            root = starting_hz
        else:
            root = starting_hz * ((3 / 2) ** i)

        while root > octave:
            root = root / 2

        third = root * (5 / 4)
        while third > octave:
            third = third / 2

        fifth = root * (3 / 2)
        while third > octave:
            fifth = fifth / 2

        frequencies[i] = [root, third, fifth]
    return frequencies


# python morning_sound_bath --duration_in_minutes 90
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration_in_minutes", type=int, required=True)
    args = parser.parse_args()

    alles.reset()  # just in case, before we start ..

    start_time = dt.datetime.now()
    weekday = dt.datetime.today().weekday()
    end_time = start_time + dt.timedelta(minutes=args.duration_in_minutes)
    total_duration_minutes = args.duration_in_minutes

    c = 256
    volume_modifier = 0.025
    hz_octaves = [1, 2, 4]
    num_oscs = 6
    num_speakers = 3
    time_to_sleep = 300

    frequencies = make_just_intonation_chords(c)
    print(frequencies[weekday])

    all_events = []
    max_start_time = 0
    while (max_start_time / 60) < total_duration_minutes:
        hz_to_play = get_frequencies(hz_octaves, frequencies[weekday])
        if all_events:
            ends_of_notes = [event[0] + event[1] for event in all_events]
            start_offset = max(ends_of_notes)
        else:
            start_offset = 0

        start_times = []
        for hz in hz_to_play:
            num_attacks = random.randint(3, 10)
            duration_for_all_attacks = random.randint(60, 240)
            durations = get_durations(num_attacks, duration_for_all_attacks)
            starts_and_durations = get_start_times(durations, start_offset)
            times_and_note = add_notes(starts_and_durations, hz)
            all_events.extend(times_and_note)

            start_times.append(starts_and_durations[-1][0])
            max_start_time = max(start_times)

    # sort by start time
    sorted_events = sorted(all_events, key=lambda event: event[0])
    print(sorted_events)

    current_time = 0
    osc_id = 0
    for start, duration, note in sorted_events:
        if start <= current_time:
            now = dt.datetime.now()
            velocity = elapsed_time_to_velocity(now, start_time, total_duration_minutes)
            note = Note(note, velocity, volume_modifier, duration)
            # play our starting note(s)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)
        else:
            # sleep until the next start time, and then play it!
            time_to_current = start - current_time
            time.sleep(time_to_current)
            current_time += time_to_current
            now = dt.datetime.now()
            velocity = elapsed_time_to_velocity(now, start_time, total_duration_minutes)
            note = Note(note, velocity, volume_modifier, duration)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)
