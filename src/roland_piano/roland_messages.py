from dataclasses import InitVar, dataclass, field
import logging
import mido
from .roland_instruments import Instruments
from .roland_address_map import RolandAddressMap
from .roland_utils import (
    ROLAND_ID_BYTES,
    InvalidMessageException,
    RolandCmd,
    get_checksum,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass
class RolandMessageRequest:
    register: RolandAddressMap
    cmd: RolandCmd
    data_as_int: int = None

    @staticmethod
    def int_to_byte(num):
        return num.to_bytes(1, byteorder="big")

    @property
    def data_as_bytes(self):
        parsers = {
            "sequencerTempoWO": lambda x: self.int_to_byte((x & 0xFF80) >> 7) + self.int_to_byte(x & 0x7F),
            "keyTransposeRO": lambda x: self.int_to_byte(x + 64),
            "toneForSingle": lambda x: self.int_to_byte((x & 0xFF000) >> 16) + b"\00" + self.int_to_byte(x & 0xFF),
        }

        if self.register.name in parsers:
            ret = parsers[self.register.name](self.data_as_int)
            logger.debug(ret, self.data_as_int)
            return ret
        else:
            return self.int_to_byte(self.data_as_int)

    def __post_init__(self):
        if self.cmd == RolandCmd.WRITE:
            if self.data_as_int is None:
                logger.error(f'Data for {RolandCmd.write} message cannot be "None"')
            self.data = self.data_as_bytes
        else:
            self.data = self.register.size
        self.checksum = get_checksum(self.register, self.data)

    @property
    def as_mido_message(self) -> mido.Message:
        return mido.Message(
            "sysex",
            data=bytearray(ROLAND_ID_BYTES + self.cmd.value + self.register.address + self.data + self.checksum),
        )


@dataclass
class RolandMessageResponse:
    message: InitVar[mido.Message]
    register: RolandAddressMap = field(init=False)
    data: bytes = field(init=False)

    def parse_data(self):
        parsers = {
            "sequencerTempoRO": lambda data: (data[1] & b"\x7F"[0]) | ((data[0] & b"\x7F"[0]) << 7),
            "keyTransposeRO": lambda x: x[0] - 64,
            "toneForSingle": lambda x: Instruments((x[0], x[2])),
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
        if self.register.name in parsers:
            ret = parsers[self.register.name](self.data)
            logger.debug(f"{self.register.name=}, {ret=}, {self.data=}")
            return ret
        else:
            return int.from_bytes(self.data, byteorder="big")

    def __post_init__(self, message: mido.Message):
        roland_id = b"".join(map(lambda i: i.to_bytes(1, "little"), message.data[0:6]))
        #  TODO: check if message starts with F07E10060241, this indicates model id
        if roland_id != ROLAND_ID_BYTES:
            raise InvalidMessageException(f"id bytes mismatch from roland_id: {roland_id=} {message=} {message.hex()}")
        # cmd = RolandCmd(message.data[6].to_bytes(1, "big"))
        self.register = RolandAddressMap(bytes(message.data[7 : 7 + 4]))
        msg_len = len(message.data)
        self.data = b"".join(d.to_bytes(1, "big") for d in message.data[11 : msg_len - 1])
        received_checksum = message.data[msg_len - 1].to_bytes(1, "big")
        checksum = get_checksum(self.register, self.data)
        if received_checksum != checksum:
            raise InvalidMessageException(f"Checksum mismatch, {received_checksum=} {self.checksum}")
        pass
