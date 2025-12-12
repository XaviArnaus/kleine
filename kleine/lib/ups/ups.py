from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.ups.INA219 import INA219

import time

class Ups(PyXavi):

    ups: INA219 = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Ups, self).init_pyxavi(config=config, params=params)

        # Initialise the INA219 UPS HAT
        self._xlog.info("Initialising INA219 UPS HAT...")
        self.ups = INA219(addr=0x43)
    
    def test(self):
        self._xlog.info("INA219 UPS HAT test")

        try:
            while True:
                bus_voltage = self.ups.getBusVoltage_V()             # voltage on V- (load side)
                shunt_voltage = self.ups.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
                current = self.ups.getCurrent_mA()                   # current in mA
                power = self.ups.getPower_W()                        # power in W
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