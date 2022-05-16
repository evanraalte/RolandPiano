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
Please look at the unit tests on how to use the library. The main difference is that the imports are handled as if you installed the library with Pip:

```python
from roland_piano import RolandPiano, discover, RolandAddressMap, Instruments
```

# Limitations
- Doesn't trigger events (e.g. volume changed) over midi when changing many of the piano settings. Connecting with the app enables this, so I  (or you😃) need to do some digging on how this is achieved. Contact me for more information on what I have tried so far.
- API is quite limited at the moment, but there is some low hanging fruit for more functionality.

