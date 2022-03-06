import mido
import time
from dataclasses import dataclass, field, InitVar
from enum import Enum
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

RolandAddressMap = Enum(
    "RolandAddressMap",
    {
        # 010000xx
        "serverSetupFileName": b"\x01\x00\x00\x00",
        # 010001xx
        "songToneLanguage": b"\x01\x00\x01\x00",
        "keyTransposeRO": b"\x01\x00\x01\x01",
        "songTransposeRO": b"\x01\x00\x01\x02",
        "sequencerStatus": b"\x01\x00\x01\x03",
        "sequencerMeasure": b"\x01\x00\x01\x05",
        "sequencerTempoNotation": b"\x01\x00\x01\x07",
        "sequencerTempoRO": b"\x01\x00\x01\x08",
        "sequencerBeatNumerator": b"\x01\x00\x01\x0A",
        "sequencerBeatDenominator": b"\x01\x00\x01\x0B",
        "sequencerPartSwAccomp": b"\x01\x00\x01\x0C",
        "sequencerPartSwLeft": b"\x01\x00\x01\x0D",
        "sequencerPartSwRight": b"\x01\x00\x01\x0E",
        "metronomeStatus": b"\x01\x00\x01\x0F",
        "headphonesConnection": b"\x01\x00\x01\x10",
        # 010002xx
        "keyBoardMode": b"\x01\x00\x02\x00",
        "splitPoint": b"\x01\x00\x02\x01",
        "splitOctaveShift": b"\x01\x00\x02\x02",
        "splitBalance": b"\x01\x00\x02\x03",
        "dualOctaveShift": b"\x01\x00\x02\x04",
        "dualBalance": b"\x01\x00\x02\x05",
        "twinPianoMode": b"\x01\x00\x02\x06",
        "toneForSingle": b"\x01\x00\x02\x07",
        "toneForSplit": b"\x01\x00\x02\x0A",
        "toneForDual": b"\x01\x00\x02\x0D",
        "songNumber": b"\x01\x00\x02\x10",
        "masterVolume": b"\x01\x00\x02\x13",
        "masterVolumeLimit": b"\x01\x00\x02\x14",
        "allSongPlayMode": b"\x01\x00\x02\x15",
        "splitRightOctaveShift": b"\x01\x00\x02\x16",
        "dualTone1OctaveShift": b"\x01\x00\x02\x17",
        "masterTuning": b"\x01\x00\x02\x18",
        "ambience": b"\x01\x00\x02\x1A",
        "headphones3DAmbience": b"\x01\x00\x02\x1B",
        "brilliance": b"\x01\x00\x02\x1C",
        "keyTouch": b"\x01\x00\x02\x1D",
        "transposeMode": b"\x01\x00\x02\x1E",
        "metronomeBeat": b"\x01\x00\x02\x1F",
        "metronomePattern": b"\x01\x00\x02\x20",
        "metronomeVolume": b"\x01\x00\x02\x21",
        "metronomeTone": b"\x01\x00\x02\x22",
        "metronomeDownBeat": b"\x01\x00\x02\x23",
        # 010003xx
        "applicationMode": b"\x01\x00\x03\x00",
        "scorePageTurn": b"\x01\x00\x03\x02",
        "arrangerPedalFunction": b"\x01\x00\x03\x03",
        "arrangerBalance": b"\x01\x00\x03\x05",
        "connection": b"\x01\x00\x03\x06",
        "keyTransposeWO": b"\x01\x00\x03\x07",
        "songTransposeWO": b"\x01\x00\x03\x08",
        "sequencerTempoWO": b"\x01\x00\x03\x09",
        "tempoReset": b"\x01\x00\x03\x0B",
        # 010004xx
        "soundEffect": b"\x01\x00\x04\x00",
        "soundEffectStopAll": b"\x01\x00\x04\x02",
        # 010005xx
        "sequencerREW": b"\x01\x00\x05\x00",
        "sequencerFF": b"\x01\x00\x05\x01",
        "sequencerReset": b"\x01\x00\x05\x02",
        "sequencerTempoDown": b"\x01\x00\x05\x03",
        "sequencerTempoUp": b"\x01\x00\x05\x04",
        "sequencerPlayStopToggle": b"\x01\x00\x05\x05",
        "sequencerAccompPartSwToggle": b"\x01\x00\x05\x06",
        "sequencerLeftPartSwToggle": b"\x01\x00\x05\x07",
        "sequencerRightPartSwToggle": b"\x01\x00\x05\x08",
        "metronomeSwToggle": b"\x01\x00\x05\x09",
        "sequencerPreviousSong": b"\x01\x00\x05\x0A",
        "sequencerNextSong": b"\x01\x00\x05\x0B",
        # 010006xx
        "pageTurnPreviousPage": b"\x01\x00\x06\x00",
        "pageTurnNextPage": b"\x01\x00\x06\x01",
        # 010007xx
        "uptime": b"\x01\x00\x07\x00",
        # 010008xx
        "addressMapVersion": b"\x01\x00\x08\x00",
    },
)


def discover(idx: int = 0) -> str:
    logger.info("Discovering Roland pianos...")
    pianos = [
        inp for inp in mido.get_input_names() if inp.startswith("Roland Digital Piano")
    ]
    if idx > len(pianos):
        logger.error(f"invalid index ({idx}), only {len(pianos)} pianos found")
        return

    piano = pianos[idx]
    return piano


class PianoNotFoundException(Exception):
    pass


class InvalidAddressException(Exception):
    pass


@dataclass
class RolandRegister:
    register: InitVar[RolandAddressMap]
    name: str = field(init=False)
    address: int = field(init=False)
    # size: RolandRegisterSize = field(init=False)

    def __post_init__(self, register: RolandAddressMap):
        self.size = self._get_register_size(register.name)
        self.address = register.value
        self.name = register.name
        pass

    @staticmethod
    def _get_register_size(register_name: str) -> bytes:
        size_map = {  # consider implementing this to read all registers
            "serverSetupFileName": 32,
            "sequencerMeasure": 2,
            "sequencerTempoRO": 2,
            "toneForSingle": 3,
            "toneForSplit": 3,
            "toneForDual": 3,
            "songNumber": 3,
            "masterTuning": 2,
            "arrangerPedalFunction": 2,
            "sequencerTempoWO": 2,
            "uptime": 8,
        }
        if register_name in size_map:
            size = size_map[register_name]
        else:
            size = 1
        return b"\x00\x00\x00" + size.to_bytes(1, byteorder="big")


class RolandCmd(Enum):
    READ = b"\x11"
    WRITE = b"\x12"


@dataclass
class RolandMessage:
    _cmd: RolandCmd = field(init=False)
    _address: bytes = field(
        init=False,
    )
    _data: bytes = field(
        init=False,
    )
    ROLAND_ID_BYTES = b"\x41\x10\x00\x00\x00\x28"

    @property
    def checksum(self):
        total = 0
        for b in self._address:
            total += b
        for b in self._data:
            total += b
        return ((128 - (total % 128)) & 0x7F).to_bytes(1, byteorder="big")


@dataclass
class RolandMessageRequest(RolandMessage):
    register: InitVar[RolandAddressMap]
    cmd: RolandCmd
    data_as_int: int = None
    _register: RolandRegister = field(init=False)

    @staticmethod
    def int_to_byte(num):
        return num.to_bytes(1, byteorder="big")

    @property
    def data_as_bytes(self):
        parsers = {
            "sequencerTempoWO": lambda x: self.int_to_byte((x & 0xFF80) >> 7)
            + self.int_to_byte(x & 0x7F),
            "keyTransposeRO": lambda x: self.int_to_byte(x + 64),
            # "toneForSingle" : lambda x : (x[0],x[2])
        }

        if self._register.name in parsers:
            return parsers[self._register.name](self.data_as_int)
        else:
            return self.int_to_byte(self.data_as_int)

    def __post_init__(
        self,
        register: RolandAddressMap,
    ):
        self._register = RolandRegister(register)
        self._address = self._register.address
        if self.cmd == RolandCmd.WRITE:
            if self.data_as_int is None:
                logger.error(f'Data for {RolandCmd.write} message cannot be "None"')
            self._data = self.data_as_bytes
        else:
            self._data = self._register.size
        pass

    @property
    def as_mido_message(self) -> mido.Message:
        return mido.Message(
            "sysex",
            data=bytearray(
                self.ROLAND_ID_BYTES
                + self.cmd.value
                + self._register.address
                + self._data
                + self.checksum
            ),
        )


@dataclass
class RolandMessageResponse(RolandMessage):
    message: InitVar[mido.Message]
    address: bytes = field(init=False)

    @staticmethod
    def get_instrument(mode):
        instruments = {
            "0,0": "Grand Piano 1",
            "0,1": "Grand Piano 2",
            "0,2": "Grand Piano 3",
            "0,3": "Grand Piano 4",
        }
        if mode in instruments:
            return instruments[mode]
        return f"Unknown instrument: {mode}"

    def parse_data(self):
        parsers = {
            "sequencerTempoRO": lambda data: (data[1] & b"\x7F"[0])
            | ((data[0] & b"\x7F"[0]) << 7),
            "keyTransposeRO": lambda x: x[0] - 64,
            "toneForSingle": lambda x: self.get_instrument(f"{x[0]},{x[2]}"),
            "uptime": lambda x: x[0] << 64
            | x[1] << 56
            | x[2] << 48
            | x[3] << 40
            | x[4] << 32
            | x[5] << 24
            | x[5] << 16
            | x[6] << 8
            | x[7] << 0,
        }
        if self.address.name in parsers:
            return parsers[self.address.name](self._data)
        else:
            return int.from_bytes(self._data, byteorder="big")

    @property
    def data(self):
        return self.parse_data()

    def __post_init__(self, message: mido.Message):
        roland_id = b"".join(map(lambda i: i.to_bytes(1, "little"), message.data[0:6]))
        assert roland_id == self.ROLAND_ID_BYTES
        self.cmd = RolandCmd(message.data[6].to_bytes(1, "big"))
        self.address = RolandAddressMap(bytes(message.data[7 : 7 + 4]))
        self._address = self.address.value
        msg_len = len(message.data)
        self._data = b"".join(
            d.to_bytes(1, "big") for d in message.data[11 : msg_len - 1]
        )
        received_checksum = message.data[msg_len - 1].to_bytes(1, "big")
        assert received_checksum == self.checksum
        pass


class RolandPiano:
    last_message = None

    contents = None
    checklist = None

    def metronome_toggle(self):
        self.write_register(RolandAddressMap.metronomeSwToggle, 0)

    def metronome_set_bpm(self, bpm: int):
        self.write_register(RolandAddressMap.sequencerTempoWO, bpm)

    def metronome_get_bpm(self) -> int:
        return self.read_register(RolandAddressMap.sequencerTempoRO)

    def volume_set_percent(self, volume: int):
        self.write_register(RolandAddressMap.masterVolume, volume)

    def volume_get_percent(self) -> int:
        return self.read_register(RolandAddressMap.masterVolume)

    def __init__(self, name: str) -> None:
        self.last_message = None
        self.contents = {}
        self.checklist = set()
        try:
            self.port: mido.ports.IOPort = mido.open_ioport(
                name=name, virtual=False, callback=self.handler
            )
        except OSError:
            raise PianoNotFoundException()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.port.close()

    def handler(self, message):
        # import debugpy

        # debugpy.debug_this_thread()
        if message.type == "sysex":
            self.last_message = RolandMessageResponse(message)
            logger.debug(f"{self.last_message.address.name}: {self.last_message.data}")
            self.contents[self.last_message.address.name] = self.last_message.data
            self.checklist.add(self.last_message.address.name)

        else:
            logger.debug(message)
        pass

    def _send(self, msg: RolandMessageRequest):
        self.port.send(msg.as_mido_message)

    def send(self, msg: mido.Message):
        self.port.send(msg)

    def read_register(self, register: RolandAddressMap):
        message = RolandMessageRequest(register=register, cmd=RolandCmd.READ)
        self._send(message)
        time_start = time.time()
        value_updated = False
        while time.time() < time_start + 1 or value_updated:
            value_updated = register.name in self.checklist
            if value_updated:
                self.checklist.remove(register.name)
                return self.contents[register.name]
            time.sleep(0.05)
        logger.error("timed out waiting for response")

    def write_register(self, register: RolandAddressMap, value: int):
        message = RolandMessageRequest(
            register=register, cmd=RolandCmd.WRITE, data_as_int=value
        )
        self._send(message)
