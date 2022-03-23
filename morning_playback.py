import datetime as dt
import time

import alles


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
    alles.reset()
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
