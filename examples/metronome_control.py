import time
from roland_piano.roland_piano import discover, RolandPiano

piano_name = discover()
with RolandPiano(piano_name) as piano:
    # toggle metronome, todo: find way to obtain state of metronome
    piano.metronome_toggle()
    for i in range(50, 200):
        piano.metronome_set_bpm(i)
        print(f"Readback volume: {piano.metronome_get_bpm()}")
        time.sleep(0.5)
