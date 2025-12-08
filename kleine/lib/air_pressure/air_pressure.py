from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .LPS22HB import LPS22HB, LPS_PRESS_OUT_XL, LPS_PRESS_OUT_L, LPS_PRESS_OUT_H, LPS_TEMP_OUT_L, LPS_TEMP_OUT_H, LPS_STATUS
import time

class AirPressure(PyXavi):
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(AirPressure, self).init_pyxavi(config=config, params=params)
    
    def test(self):

        self._xlog.info("🚀 Starting Air Pressure test run...")
        
        PRESS_DATA = 0.0
        TEMP_DATA = 0.0
        u8Buf=[0,0,0]
        print("\nPressure Sensor Test Program ...\n")
        lps22hb=LPS22HB()
        while True:
            try:
                time.sleep(0.1)
                lps22hb.LPS22HB_START_ONESHOT()
                if (lps22hb._read_byte(LPS_STATUS)&0x01)==0x01:  # a new pressure data is generated
                    u8Buf[0]=lps22hb._read_byte(LPS_PRESS_OUT_XL)
                    u8Buf[1]=lps22hb._read_byte(LPS_PRESS_OUT_L)
                    u8Buf[2]=lps22hb._read_byte(LPS_PRESS_OUT_H)
                    PRESS_DATA=((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0
                if (lps22hb._read_byte(LPS_STATUS)&0x02)==0x02:   # a new pressure data is generated
                    u8Buf[0]=lps22hb._read_byte(LPS_TEMP_OUT_L)
                    u8Buf[1]=lps22hb._read_byte(LPS_TEMP_OUT_H)
                    TEMP_DATA=((u8Buf[1]<<8)+u8Buf[0])/100.0
                print('Pressure = %6.2f hPa , Temperature = %6.2f °C\r\n'%(PRESS_DATA,TEMP_DATA))
            except(KeyboardInterrupt):
                print("\n") 
                break 

