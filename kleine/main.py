from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.accelerometer.accelerometer import Accelerometer
from kleine.lib.air_pressure.air_pressure import AirPressure
from kleine.lib.temperature.temperature import Temperature

class Main(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

    def run(self):

        self._xlog.info("🚀 Starting Kleine main run...")

        self._xlog.debug("Test accelerometer...")
        accelerometer = Accelerometer()
        accelerometer.test()

        self._xlog.debug("Test air pressure...")
        air_pressure = AirPressure()
        air_pressure.test()

        self._xlog.debug("Test temperature...")
        temperature = Temperature()
        temperature.test()

        # However it happened, just close nicely.
        self.close_nicely()
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely...")
