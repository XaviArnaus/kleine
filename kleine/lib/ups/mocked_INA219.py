from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class MockedINA219(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(MockedINA219, self).init_pyxavi(config=config, params=params)

    def getBusVoltage_V(self):
        # Mocked voltage reading
        return 12.0

    def getCurrent_mA(self):
        # Mocked current reading
        return 1.0

    def getPower_mW(self):
        # Mocked power reading
        return self.getBusVoltage_V() * self.getCurrent_mA()
    
    def getShuntVoltage_mV(self):
        # Mocked shunt voltage reading
        return 0.1
    
    def getPower_W(self):
        return self.getPower_mW() / 1000.0

    def close(self):
        pass