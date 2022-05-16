import mido
import time
from .roland_messages import RolandMessageRequest, RolandMessageResponse
from .roland_instruments import Instruments
from .roland_address_map import RolandAddressMap
from .roland_utils import (
    InvalidMessageException,
    PianoNotFoundException,
    RolandCmd,
)
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RolandPiano:
    last_message = None

    contents = None
    checklist = None

    instances = set()

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

    def get_instrument(self) -> Instruments:
        return self.read_register(RolandAddressMap.toneForSingle)

    def set_instrument(self, instrument: Instruments):
        value = (instrument.value[0] << 16) | instrument.value[1]
        self.write_register(RolandAddressMap.toneForSingle, value)

    def __init__(self, name: str) -> None:
        self.last_message = None
        self.contents = {}
        self.checklist = set()
        try:
            self.port: mido.ports.IOPort = mido.open_ioport(name=name, virtual=False, callback=self.handler)
        except OSError:
            raise PianoNotFoundException()
        self.write_register(RolandAddressMap.connection, 1)
        # official setup routine, but not fixing push status on change
        # self.read_register(RolandAddressMap.uptime)
        # self.read_register(RolandAddressMap.addressMapVersion)
        # self.send_mido_msg(mido.Message("sysex", data=[0x7E, 0x10, 0x06, 0x01]))
        # self.read_register(RolandAddressMap.serverSetupFileName)
        # self.read_register(RolandAddressMap.sequencerStatus)
        # self.read_register(RolandAddressMap.metronomeStatus)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.port.reset()
        self.port.close()
        while not self.port.closed:
            time.sleep(0.1)
        time.sleep(2)

    def handler(self, message):

        # import debugpy

        # debugpy.debug_this_thread()

        if message.type == "sysex":
            logger.debug(f"handler: raw sysex: {message}")
            try:
                self.last_message = RolandMessageResponse(message)
                data = self.last_message.parse_data()
                logger.debug(f"{self.last_message.register.name}: {data}")
                self.contents[self.last_message.register.name] = data
                self.checklist.add(self.last_message.register.name)
            except InvalidMessageException as e:
                logger.error(e)
        else:
            logger.debug(f"handler: nonsysex msg: {message}")
        pass

    def send_mido_msg(self, msg: mido.Message):
        logger.debug(f"send: {msg}, hex: {msg.hex()}")
        self.port.send(msg)

    def read_register(self, register: RolandAddressMap):
        logger.debug(f"read register {register}")
        message = RolandMessageRequest(register=register, cmd=RolandCmd.READ)
        self.send_mido_msg(message.as_mido_message)
        time_start = time.time()
        value_updated = False
        while (time.time() < time_start + 1) or value_updated:
            value_updated = register.name in self.checklist
            if value_updated:
                self.checklist.remove(register.name)
                return self.contents[register.name]
            time.sleep(0.05)
        logger.error("timed out waiting for response")

    def write_register(self, register: RolandAddressMap, value: int):
        logger.debug(f"write register {register}, {value}")
        message = RolandMessageRequest(register=register, cmd=RolandCmd.WRITE, data_as_int=value)
        logger.debug(message.as_mido_message.hex())
        self.send_mido_msg(message.as_mido_message)
