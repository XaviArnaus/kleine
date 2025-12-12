from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

# from kleine.lib.eink.eink import Eink
# from kleine.lib.eink.macros import Macros
from kleine.lib.accelerometer.accelerometer import Accelerometer
from kleine.lib.air_pressure.air_pressure import AirPressure
from kleine.lib.temperature.temperature import Temperature
from kleine.lib.lcd.lcd import Lcd

import time

class Main(PyXavi):

    # eink: Eink = None
    # macros: Macros = None
    accelerometer: Accelerometer = None
    air_pressure: AirPressure = None
    temperature: Temperature = None
    lcd: Lcd = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

        # Initialise the LCD display
        self._xlog.info("Initialising LCD display...")
        self.lcd = Lcd(config=self._xconfig, params=self._xparams)

        # # Initialise the eInk display
        # self._xlog.info("Initialising eInk display...")
        # self.eink = Eink(config=self._xconfig, params=self._xparams)
        # self.macros = Macros(config=self._xconfig, params=self._xparams)

        # Initialise the accelerometer
        self._xlog.info("Initialising accelerometer...")
        self.accelerometer = Accelerometer(config=self._xconfig, params=self._xparams)

        # Initialise the air pressure sensor
        self._xlog.info("Initialising air pressure sensor...")
        self.air_pressure = AirPressure(config=self._xconfig, params=self._xparams)

        # Initialise the temperature sensor
        self._xlog.info("Initialising temperature sensor...")
        self.temperature = Temperature(config=self._xconfig, params=self._xparams)

    def run(self):

        self._xlog.info("🚀 Starting Kleine main run...")

        # self.macros.startup_splash(display=self.eink)
        self.lcd.test()
        time.sleep(2)

        self._xlog.debug("Test accelerometer...")
        self.accelerometer.test()

        self._xlog.debug("Test air pressure...")
        self.air_pressure.test()

        self._xlog.debug("Test temperature...")
        self.temperature.test()

        # However it happened, just close nicely.
        self.close_nicely()
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely...")

        # Clear the Display
        # self.macros.soft_clear(display=self.eink)
        # self.eink.clear()

        # # Sleep the eInk
        # self.eink.close()
