python morning_sound_bath.py --duration_in_minutes 75 &
caffeinate -w $(ps aux | grep "[m]orning_sound_bath" | awk '{print $2}')
