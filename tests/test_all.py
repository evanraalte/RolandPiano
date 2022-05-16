import time
import unittest
from src.roland_piano import RolandPiano, discover, RolandAddressMap, Instruments
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%S",
)


class TestModule(unittest.TestCase):
    def test_metronome_status(self):
        piano_name = discover()
        with RolandPiano(piano_name) as piano:
            status = piano.read_register(RolandAddressMap.metronomeStatus)

            logging.info(f"Status is: {status}")
            logging.info("Setting volume to 10")
            piano.volume_set_percent(10)
            logging.info("Toggling metronome")
            piano.metronome_toggle()

            updated = False
            start_time = time.time()
            while not updated and time.time() < start_time + 2:
                time.sleep(0.1)
                if piano.read_register(RolandAddressMap.metronomeStatus) == status:
                    logging.info("Waiting...")
                else:
                    logging.info("Updated!")
                    updated = True
            self.assertTrue(updated)

            if status == 0:
                logging.info("Turning off metronome..")
                piano.metronome_toggle()  # disable metronome if it was off

    def test_volume_range(self):
        piano_name = discover()
        with RolandPiano(piano_name) as piano:
            for i in [0, 25, 50, 75, 100]:
                logging.info(f"Setting volume to {i}")
                piano.volume_set_percent(i)
                self.assertEqual(piano.volume_get_percent(), i)

    def test_volume_not_update_when_connection_disabled(self):
        piano_name = discover()
        with RolandPiano(piano_name) as piano:
            logging.info("Setting volume to 1")
            piano.volume_set_percent(1)
            self.assertEqual(piano.volume_get_percent(), 1)

            logging.info("Disable connection so that the volume is not updated any longer")
            piano.write_register(RolandAddressMap.connection, 0)
            for i in [0, 25, 50, 75, 100]:
                logging.info(f"'Setting' volume to {i}")
                piano.volume_set_percent(i)
                # Piano reports false positive with a write after read when connection is 0
                time.sleep(0.5)
                self.assertEqual(piano.volume_get_percent(), 1)

    def test_set_instrument(self):
        piano_name = discover()
        with RolandPiano(piano_name) as piano:
            for instrument in Instruments:
                logging.info(f"Setting instrument to {instrument}")
                piano.set_instrument(instrument)
                logging.info(f"Get instrument: {piano.get_instrument()}")


if __name__ == "__main__":
    unittest.main()
