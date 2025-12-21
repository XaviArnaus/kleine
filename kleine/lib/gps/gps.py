from pyxavi import Config, Dictionary, dd
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.gps.mocked_serial import MockedSerial
from kleine.lib.utils.calculations import Calculations

class GPS(PyXavi):

    driver: MockedSerial = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(GPS, self).init_pyxavi(config=config, params=params)

        if self._xconfig.get("gps.mock", True):
            self.driver = MockedSerial(config=config, params=params)
        else:
            from kleine.lib.gps.nmea_reader import NMEAReader
            self.driver = NMEAReader(config=config, params=params)
    
    def close(self):
        self.driver.close()

    def get_position(self) -> dict | None:
        data = self.driver.get_gps_data()
        dd({
            # Incoming from GGA
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "direction_latitude": data.get("direction_latitude"),
            "direction_longitude": data.get("direction_longitude"),
            "interval": data.get("interval"),
            "altitude": data.get("altitude"),
            "altitude_units": data.get("altitude_units"),
            "timestamp": data.get("timestamp"),
            "status": data.get("status"),
            "signal_quality": data.get("signal_quality"),
            # Unmerged from RMC
            "speed": data.get("speed"),
            "heading": data.get("heading"),
        })
        return data