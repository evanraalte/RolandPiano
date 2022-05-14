import time
from roland_piano.roland_piano import discover, RolandPiano

piano_name = discover()
with RolandPiano(piano_name) as piano:
    for i in range(0, 100):
        piano.volume_set_percent(i)
        print(f"Readback Volume: {piano.volume_get_percent()}")
        time.sleep(0.5)
