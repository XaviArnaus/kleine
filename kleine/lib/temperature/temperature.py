from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .SHTC3 import SHTC3, SHTC3_I2C_ADDRESS
import time

class Temperature(PyXavi):
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Temperature, self).init_pyxavi(config=config, params=params)

    def test(self):

        self._xlog.info("🚀 Starting Temperature test run...")

        try:
            shtc3 = SHTC3(1, SHTC3_I2C_ADDRESS)
            
            while True:
                print("Temperature = %6.2f°C , Humidity = %6.2f%%" % (shtc3.SHTC3_Read_TH(),shtc3.SHTC3_Read_RH()))

        except(KeyboardInterrupt):
                print("\n")

