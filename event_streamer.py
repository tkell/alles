import math
import random


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
            start_time = 0 + start_offset
        else:
            start_time = sum(durations[0:i]) + start_offset
        starts_and_durations.append((start_time, duration))
    return starts_and_durations


def add_notes(starts_and_durations, hz, volume):
    return [(s_d[0], s_d[1], hz, volume) for s_d in starts_and_durations]


def add_velocity(events, total_duration_minutes):
    with_velocity = []
    for (start_time, duration, hz, volume) in events:
        velocity = start_time_to_velocity(start_time, total_duration_minutes)
        with_velocity.append((start_time, duration, hz, volume, velocity))
    return with_velocity


def start_time_to_velocity(start_time_seconds, total_duration_minutes):
    current_seconds = start_time_seconds
    total_duration_seconds = total_duration_minutes * 60
    if current_seconds > total_duration_seconds:
        return 0
    old_range = total_duration_seconds
    new_range = math.pi
    zero_to_pi = (((current_seconds - 0) * new_range) / old_range) + 0
    sine_value = math.sin(zero_to_pi)
    return sine_value


def make_all_events(root_note, octaves_and_volumes, total_duration_minutes, weekday):
    roots = make_just_roots(root_note)
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
            with_velocity = add_velocity(times_and_note, total_duration_minutes)

            all_events.extend(with_velocity)
            ## ok, so these are (start_time, duration, hz, volume, velocity)
            ## and that is start_time relative to 0, not relative to "real time"
            start_times.append(starts_and_durations[-1][0])
            max_start_time = max(start_times)

    # sort by start time
    sorted_events = sorted(all_events, key=lambda event: event[0])
    return sorted_events
