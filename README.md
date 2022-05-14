# Roland Piano
Library for interfacing with Roland FP pianos over midi. Tested on both Mac and Linux.

# Installation
Run:
```bash
python3 -m pip install roland-piano
```

# How this started
I found the button only interface on my Roland FP-10 somewhat limiting. The app would give more insight, but was a bit too buggy IMO. Hence I decided to reverse engineer the Roland specific midi messages and create a Python API so that people can build their own interface. Feel free to contribute!

# Examples
Setting and reading the volume.
```python
import time
from roland_piano.roland_piano import discover, RolandPiano

piano_name = discover()
with RolandPiano(piano_name) as piano:
    for i in range(0, 100):
        piano.volume_set_percent(i)
        print(f"Readback Volume: {piano.volume_get_percent()}")
        time.sleep(0.5)
```

Togle metronome and increase the BPM
```python
import time
from roland_piano.roland_piano import discover, RolandPiano

piano_name = discover()
with RolandPiano(piano_name) as piano:
    # toggle metronome, todo: find way to obtain state of metronome
    piano.metronome_toggle()
    for i in range(50, 200):
        piano.metronome_set_bpm(i)
        print(f"Readback BPM: {piano.metronome_get_bpm()}")
        time.sleep(0.5)
```

# Limitations
- Doesn't trigger events (e.g. volume changed) over midi when changing many of the piano settings. Connecting with the app enables this, so I  (or you😃) need to do some digging on how this is achieved. Contact me for more information on what I have tried so far.
- API is limited to metronome and volume at the moment, but there is some low hanging fruit for more functionality.

