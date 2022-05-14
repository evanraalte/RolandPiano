from roland_piano.roland_piano import discover, RolandPiano, Instruments

piano_name = discover()
with RolandPiano(piano_name) as piano:
    for instrument in Instruments:
        if instrument == Instruments.UNKNOWN:
            continue
        print(f"Setting instrument to {instrument}")
        piano.set_instrument(instrument)
        print(f"Get instrument: {piano.get_instrument()}")
