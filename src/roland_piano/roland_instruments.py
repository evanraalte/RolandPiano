from enum import Enum
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Instruments(Enum):
    GRAND_PIANO_1 = (0, 0)
    GRAND_PIANO_2 = (0, 1)
    GRAND_PIANO_3 = (0, 2)
    GRAND_PIANO_4 = (0, 3)
    RAGTIME_PIANO = (0, 4)
    HARPSICHORD_1 = (0, 5)
    HARPSICHORD_2 = (0, 6)

    E_PIANO_1 = (1, 0)
    E_PIANO_2 = (1, 1)
    E_PIANO_3 = (1, 2)
    CLAV = (1, 3)
    VIBRAPHONE = (1, 4)
    CELESTA = (1, 5)
    SYNTH_BELL = (1, 6)

    STRINGS_1 = (2, 0)
    STRINGS_2 = (2, 1)
    HARP = (2, 2)
    JAZZ_ORGAN_1 = (2, 3)
    JAZZ_ORGAN_2 = (2, 4)
    CHURCH_ORGAN1 = (2, 5)
    CHURCH_ORGAN2 = (2, 6)
    ACCORDION = (2, 7)
    CHOIR_1 = (2, 8)
    JAZZ_SCAT = (2, 9)
    CHOIR_2 = (2, 10)
    CHOIR_3 = (2, 11)
    SYNTH_PAD = (2, 12)
    NYLON_STR_GTR = (2, 13)
    STEEL_STR_GTR = (2, 14)
    DECAY_STRINGS = (2, 15)
    DECAY_CHOIR = (2, 16)
    DECAY_CHOIR_PAD = (2, 17)
    ACOUSTIC_BASS = (2, 18)
    ABASS_CYMBAL = (2, 19)
    FINGERED_BASS = (2, 20)
    THUM_VOICE = (2, 21)

    @classmethod
    def _missing_(cls, value):
        logger.error(f"Unknown instrument: {value}")
