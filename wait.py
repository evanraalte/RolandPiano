from src.roland_piano import (
    discover,
    RolandPiano,
)
import logging
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%S",
)

piano_name = discover()
with RolandPiano(piano_name) as piano:
    while True:
        time.sleep(1)
