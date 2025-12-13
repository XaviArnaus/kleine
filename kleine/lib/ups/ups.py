from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.ups.mocked_INA219 import MockedINA219

import time

class Ups(PyXavi):

    driver: MockedINA219 = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Ups, self).init_pyxavi(config=config, params=params)

        # Initialise the INA219 UPS HAT
        self._xlog.info("Initialising INA219 UPS HAT.")
        if self._xconfig.get("ups.mock", False):
            self._xlog.warning("Using mocked INA219 driver")
            self.driver = MockedINA219(config=self._xconfig, params=self._xparams)
        else:
            self._xlog.info("Using real INA219 driver")
            from kleine.lib.ups.INA219 import INA219
            self.driver = INA219(
                i2c_bus=self._xconfig.get("ups.hardware.bus", 1), 
                addr=self._xconfig.get("ups.hardware.address", 0x43))

    def get_battery_percentage(self) -> float:
        bus_voltage = self.driver.getBusVoltage_V()
        p = (bus_voltage - 3)/1.2*100
        if(p > 100):p = 100
        if(p < 0):p = 0
        return p
    
    def is_charging(self) -> bool:
        current = self.driver.getCurrent_mA()
        return current > 0
    
    def close(self):
        self.driver.close()

    def test(self):
        self._xlog.info("INA219 UPS HAT test")

        try:
            while True:
                bus_voltage = self.driver.getBusVoltage_V()             # voltage on V- (load side)
                shunt_voltage = self.driver.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
                current = self.driver.getCurrent_mA()                   # current in mA
                power = self.driver.getPower_W()                        # power in W
                p = (bus_voltage - 3)/1.2*100
                if(p > 100):p = 100
                if(p < 0):p = 0

                # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
                # print("PSU Voltage:   {:6.3f} V".format(bus_voltage + shunt_voltage))
                # print("Shunt Voltage: {:9.6f} V".format(shunt_voltage))
                print("Load Voltage:  {:6.3f} V".format(bus_voltage))
                print("Current:       {:6.3f} A".format(current/1000))
                print("Charging?      {}".format("True" if current > 0 else "False"))
                print("Power:         {:6.3f} W".format(power))
                print("Percent:       {:3.1f}%".format(p))
                print("")

                time.sleep(2)
        except KeyboardInterrupt:
            return