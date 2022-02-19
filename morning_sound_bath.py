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
        octave, volume_modifier = random.choice(octaves)
        hz = frequency * octave
        final_hz.append((hz, volume_modifier))
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


def add_notes(starts_and_durations, hz, volume):
    return [(s_d[0], s_d[1], hz, volume) for s_d in starts_and_durations]


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


def run_sound_bath(args):
    # wait for the right time to run
    daily_start_time = dt.datetime.strptime(args.start_time, "%H%M")
    total_duration_minutes = args.duration_in_minutes
    daily_end_time = daily_start_time + dt.timedelta(minutes=total_duration_minutes)

    now = dt.datetime.now()
    start_time_today = now.replace(
        hour=daily_start_time.hour, minute=daily_start_time.minute
    )
    end_time_today = now.replace(hour=daily_end_time.hour, minute=daily_end_time.minute)
    while now < start_time_today or now > end_time_today:
        time.sleep(300)
        now = dt.datetime.now()
        start_time_today = now.replace(
            hour=daily_start_time.hour, minute=daily_start_time.minute
        )
        end_time_today = now.replace(
            hour=daily_end_time.hour, minute=daily_end_time.minute
        )

    # reset and start!
    alles.reset()
    start_time = dt.datetime.now()
    weekday = dt.datetime.today().weekday()
    end_time = start_time + dt.timedelta(minutes=total_duration_minutes)
    total_duration_minutes = args.duration_in_minutes

    c = 192  # totally not a C, but might give me a good balance of high / low hz:
    octaves_and_volumes = [(1, 0.025), (2, 0.012), (4, 0.006)]
    num_oscs = 6
    num_speakers = 3
    roots = make_just_roots(c)

    all_events = []
    max_start_time = 0
    while (max_start_time / 60) < total_duration_minutes:
        root = roots[weekday]
        frequencies = make_just_intonation_chords(root)
        hz_and_volumes = get_frequencies(octaves_and_volumes, frequencies)
        if all_events:
            ends_of_notes = [event[0] + event[1] for event in all_events]
            start_offset = max(ends_of_notes)
        else:
            start_offset = 0

        start_times = []
        for hz, volume in hz_and_volumes:
            num_attacks = random.randint(3, 10)
            duration_for_all_attacks = random.randint(60, 240)
            durations = get_durations(num_attacks, duration_for_all_attacks)
            starts_and_durations = get_start_times(durations, start_offset)
            times_and_note = add_notes(starts_and_durations, hz, volume)
            all_events.extend(times_and_note)

            start_times.append(starts_and_durations[-1][0])
            max_start_time = max(start_times)

    # sort by start time
    sorted_events = sorted(all_events, key=lambda event: event[0])

    current_time = 0
    osc_id = 0
    for start, duration, note, volume in sorted_events:
        if start <= current_time:
            now = dt.datetime.now()
            velocity = elapsed_time_to_velocity(now, start_time, total_duration_minutes)
            note = Note(note, velocity, volume, duration)
            # play our starting note(s)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)
        else:
            # sleep until the next start time, and then play it!
            time_to_current = start - current_time
            time.sleep(time_to_current)
            current_time += time_to_current
            now = dt.datetime.now()
            velocity = elapsed_time_to_velocity(now, start_time, total_duration_minutes)
            note = Note(note, velocity, volume, duration)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)


# python morning_sound_bath --start_time 0700 --duration_in_minutes 90
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_time", type=str, required=True)
    parser.add_argument("--duration_in_minutes", type=int, required=True)
    args = parser.parse_args()

    while True:
        run_sound_bath(args)
