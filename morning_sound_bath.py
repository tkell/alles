import argparse
import datetime as dt
import time

import event_streamer
import morning_playback


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
    morning_playback.block_and_play_events(
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
