from enum import Enum
import logging
import mido

ROLAND_ID_BYTES = b"\x41\x10\x00\x00\x00\x28"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.WARNING)


class RolandCmd(Enum):
    READ = b"\x11"
    WRITE = b"\x12"


def discover(idx: int = 0) -> str:
    logger.info("Discovering Roland pianos...")
    pianos = [inp for inp in mido.get_input_names() if inp.startswith("Roland Digital Piano")]
    if idx > len(pianos):
        logger.error(f"invalid index ({idx}), only {len(pianos)} pianos found")
        return

    piano = pianos[idx]
    return piano


class PianoNotFoundException(Exception):
    pass


class InvalidAddressException(Exception):
    pass


class InvalidMessageException(Exception):
    pass


def get_checksum(register, data):
    logger.debug(f"checksum: {register.address} {data}")
    total = 0
    for b in register.address:
        total += b
    for b in data:
        total += b
    return ((128 - (total % 128)) & 0x7F).to_bytes(1, byteorder="big")
