from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.gps.mocked_serial import MockedSerial

class GPS(PyXavi):

    driver: MockedSerial = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(GPS, self).init_pyxavi(config=config, params=params)

        if self._xconfig.get("gps.mock", True):
            self.driver = MockedSerial(config=config, params=params)
        else:
            # from kleine.lib.gps.serial import GpsSerial
            # self.driver = GpsSerial(config=config, params=params)
            from kleine.lib.gps.nmea_reader import NMEAReader
            self.driver = NMEAReader(config=config, params=params)

    def get_position(self) -> dict | None:
        return self.driver.get_gps_data()