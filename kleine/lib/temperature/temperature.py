from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .SHTC3 import SHTC3, SHTC3_I2C_ADDRESS
import time

class Temperature(PyXavi):

    CORRECTION_FACTOR = -5.0  # Adjust this value based on calibration

    driver: SHTC3 = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Temperature, self).init_pyxavi(config=config, params=params)

        self.driver = SHTC3(1, SHTC3_I2C_ADDRESS)

    def get_temperature(self) -> float:
        temperature = self.driver.SHTC3_Read_TH() + self.CORRECTION_FACTOR
        return temperature
    
    def get_humidity(self) -> float:
        humidity = self.driver.SHTC3_Read_RH()
        return humidity

    def test(self):

        self._xlog.info("🚀 Starting Temperature test run...")

        try:
            while True:
                temperature = self.get_temperature()
                humidity = self.get_humidity()
                print("Temperature = %6.2f°C , Humidity = %6.2f%%" % (temperature, humidity))

        except(KeyboardInterrupt):
                print("\n")

