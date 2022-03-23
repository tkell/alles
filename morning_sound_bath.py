import argparse
import datetime as dt

import time
from collections import deque

import alles
import event_streamer


class Note:
    def __init__(self, frequency, velocity, volume, duration):
        self.frequency = frequency
        self.velocity = velocity
        self.volume = volume
        self.duration = duration

    def __repr__(self):
        return f"<Note: {self.frequency} hz, {self.velocity} velocity>"


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


def block_and_play_events(
    sorted_events, start_time, total_duration_minutes, num_speakers, num_oscs
):
    current_time = 0
    osc_id = 0
    for start, duration, note, volume, velocity in sorted_events:
        if start <= current_time:
            now = dt.datetime.now()
            note = Note(note, velocity, volume, duration)
            # play our starting note(s)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)
        else:
            # sleep until the next start time, and then play it!
            time_to_current = start - current_time
            time.sleep(time_to_current)
            current_time += time_to_current
            now = dt.datetime.now()
            note = Note(note, velocity, volume, duration)
            osc_id = play_note(osc_id, num_oscs, num_speakers, note)


def block_until_start(daily_start_time, daily_end_time):
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
    return


def run_sound_bath(args):
    total_duration_minutes = args.duration_in_minutes
    daily_start_time = dt.datetime.strptime(args.start_time, "%H%M")
    daily_end_time = daily_start_time + dt.timedelta(minutes=total_duration_minutes)

    block_until_start(daily_start_time, daily_end_time)

    alles.reset()
    start_time = dt.datetime.now()
    weekday = dt.datetime.today().weekday()
    end_time = start_time + dt.timedelta(minutes=total_duration_minutes)
    c = 192  # totally not a C, but might give me a good balance of high / low hz:
    octaves_and_volumes = [(1, 0.025), (2, 0.012), (4, 0.006)]

    all_events = event_streamer.make_all_events(
        c, octaves_and_volumes, total_duration_minutes, weekday
    )
    num_oscs = 6
    num_speakers = 3
    block_and_play_events(
        all_events, start_time, total_duration_minutes, num_oscs, num_speakers
    )


# python morning_sound_bath --start_time 0700 --duration_in_minutes 90
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_time", type=str, required=True)
    parser.add_argument("--duration_in_minutes", type=int, required=True)
    args = parser.parse_args()

    while True:
        run_sound_bath(args)
