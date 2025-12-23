from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class MockedLPS22HB(PyXavi):
    
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(MockedLPS22HB, self).init_pyxavi(config=config, params=params)

    def LPS22HB_RESET(self):
        pass
    def LPS22HB_START_ONESHOT(self):
        pass
    def _read_byte(self,cmd):
        return 0
    def _read_u16(self,cmd):
        return 0
    def _write_byte(self,cmd,val):
        pass