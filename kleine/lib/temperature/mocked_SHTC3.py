from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class MockedSHTC3(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(MockedSHTC3, self).init_pyxavi(config=config, params=params)
    
    def SHTC3_Read_TH(self): # Read temperature 
        self._xlog.debug("MockedSHTC3: Reading temperature (mocked value)")
        return 22.5  # Mocked temperature value

    def SHTC3_Read_RH(self): # Read humidity
        self._xlog.debug("MockedSHTC3: Reading humidity (mocked value)")
        return 60.0  # Mocked humidity value