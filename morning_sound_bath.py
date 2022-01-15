import argparse
import datetime as dt

import math
import random
import time
from collections import deque
import alles


def elapsed_time_to_velocity(current_time, start_time, total_duration_minutes):
    time_elapsed = current_time - start_time
    current_minutes = time_elapsed.seconds // 60
    if current_minutes > total_duration_minutes:
        return 0
    old_range = total_duration_minutes
    new_range = math.pi
    zero_to_pi = (((current_minutes - 0) * new_range) / old_range) + 0
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


def get_start_times(durations):
    starts_and_durations = []
    for i, duration in enumerate(durations):
        if i == 0:
            starts_and_durations.append((0, duration))
        else:
            starts_and_durations.append((sum(durations[0:i]), duration))
    return starts_and_durations


def add_notes(starts_and_durations, hz):
    return [(s_d[0], s_d[1], hz) for s_d in starts_and_durations]


def play_note(
    osc_id, num_oscs, num_speakers, note, velocity, duration, volume_modifier
):
    first_breakpoint_ms = round(((duration) / 2) * 1000)
    second_breakpoint_ms = round((duration) * 1000)
    breakpoint_string = f"{first_breakpoint_ms},10,{second_breakpoint_ms},0.05,500,0"

    print("sending ... ", osc_id, note, velocity, duration, breakpoint_string)
    alles.send(
        osc=osc_id,
        bp0=breakpoint_string,
        bp0_target=alles.TARGET_AMP,
        wave=alles.TRIANGLE,
        vel=velocity,
        volume=volume_modifier,
        freq=note,
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


# python morning_sound_bath --start_time 0700 --duration_in_minutes 90
## - refactor events to use noteOff, not this "build them all at once" bit
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_time", type=str, required=True)
    parser.add_argument("--duration_in_minutes", type=int, required=True)
    args = parser.parse_args()

    start_time = dt.datetime.strptime(args.start_time, "%H%M")
    end_time = start_time + dt.timedelta(minutes=args.duration_in_minutes)
    total_duration_minutes = args.duration_in_minutes

    c = 256
    volume_modifier = 0.025
    hz_octaves = [1, 2, 4]
    num_oscs = 6
    num_speakers = 3
    time_to_sleep = 300

    while True:
        now = dt.datetime.now()
        start_time_today = now.replace(hour=start_time.hour, minute=start_time.minute)
        end_time_today = now.replace(hour=end_time.hour, minute=end_time.minute)
        weekday = dt.datetime.today().weekday()
        if now < start_time_today or now > end_time_today:
            print("nothing to do ...")
            time.sleep(time_to_sleep)
            continue
        alles.reset()  # just in case, before we start ..
        print("we're going! ")

        frequencies = make_just_intonation_chords(c)
        hz_to_play = get_frequencies(hz_octaves, frequencies[weekday])
        velocity = elapsed_time_to_velocity(
            now, start_time_today, total_duration_minutes
        )
        next_voice = random.randint(60, 240)

        all_events = []
        for hz in hz_to_play:
            num_attacks = random.randint(3, 10)
            durations = get_durations(num_attacks, next_voice)
            starts_and_durations = get_start_times(durations)
            times_and_note = add_notes(starts_and_durations, hz)
            all_events.extend(times_and_note)
        # sort by start time
        sorted_events = sorted(all_events, key=lambda event: event[0])

        current_time = 0
        osc_id = 0
        for start, duration, note in sorted_events:
            if start <= current_time:
                # play our starting note(s)
                osc_id = play_note(
                    osc_id,
                    num_oscs,
                    num_speakers,
                    note,
                    velocity,
                    duration,
                    volume_modifier,
                )
            else:
                # sleep until the next start time, and then play it!
                time_to_current = start - current_time
                time.sleep(time_to_current)
                current_time += time_to_current
                osc_id = play_note(
                    osc_id,
                    num_oscs,
                    num_speakers,
                    note,
                    velocity,
                    duration,
                    volume_modifier,
                )
