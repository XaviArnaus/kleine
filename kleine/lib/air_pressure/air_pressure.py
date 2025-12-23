from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .mocked_LPS22HB import MockedLPS22HB
import time

class AirPressure(PyXavi):

    driver: MockedLPS22HB = None
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(AirPressure, self).init_pyxavi(config=config, params=params)

        if self._xconfig.get("air_pressure.mock", False):
            self._xlog.warning("Using mocked LPS22HB driver")
            self.driver = MockedLPS22HB(config=config, params=params)
        else:
            self._xlog.info("Using real LPS22HB driver")
            from .LPS22HB import LPS22HB
            self.driver = LPS22HB()

    def get_air_pressure(self) -> float:

        if isinstance(self.driver, MockedLPS22HB):
            self._xlog.debug("Using mocked air pressure value")
            return 1013.25  # Return a standard atmospheric pressure value for mocking

        from .LPS22HB import LPS_PRESS_OUT_XL, LPS_PRESS_OUT_L, LPS_PRESS_OUT_H, LPS_STATUS
        self.driver.LPS22HB_START_ONESHOT()
        PRESS_DATA = 0.0
        u8Buf = [0, 0, 0]
        time.sleep(0.1)
        if (self.driver._read_byte(LPS_STATUS) & 0x01) == 0x01:  # a new pressure data is generated
            u8Buf[0] = self.driver._read_byte(LPS_PRESS_OUT_XL)
            u8Buf[1] = self.driver._read_byte(LPS_PRESS_OUT_L)
            u8Buf[2] = self.driver._read_byte(LPS_PRESS_OUT_H)
            PRESS_DATA = ((u8Buf[2] << 16) + (u8Buf[1] << 8) + u8Buf[0]) / 4096.0
        return PRESS_DATA
    
    def test(self):

        self._xlog.info("🚀 Starting Air Pressure test run...")
        from .LPS22HB import LPS22HB, LPS_PRESS_OUT_XL, LPS_PRESS_OUT_L, LPS_PRESS_OUT_H, LPS_TEMP_OUT_L, LPS_TEMP_OUT_H, LPS_STATUS

        temp_correction_factor = -5.0  # Adjust this value based on calibration
        
        PRESS_DATA = 0.0
        TEMP_DATA = 0.0
        u8Buf=[0,0,0]
        print("\nPressure Sensor Test Program ...\n")
        while True:
            try:
                time.sleep(0.1)
                self.driver.LPS22HB_START_ONESHOT()
                if (self.driver._read_byte(LPS_STATUS)&0x01)==0x01:  # a new pressure data is generated
                    u8Buf[0]=self.driver._read_byte(LPS_PRESS_OUT_XL)
                    u8Buf[1]=self.driver._read_byte(LPS_PRESS_OUT_L)
                    u8Buf[2]=self.driver._read_byte(LPS_PRESS_OUT_H)
                    PRESS_DATA=((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0
                if (self.driver._read_byte(LPS_STATUS)&0x02)==0x02:   # a new pressure data is generated
                    u8Buf[0]=self.driver._read_byte(LPS_TEMP_OUT_L)
                    u8Buf[1]=self.driver._read_byte(LPS_TEMP_OUT_H)
                    TEMP_DATA=((u8Buf[1]<<8)+u8Buf[0])/100.0 + temp_correction_factor
                print('Pressure = %6.2f hPa , Temperature = %6.2f °C\r\n'%(PRESS_DATA,TEMP_DATA))
            except(KeyboardInterrupt):
                print("\n") 
                break 

