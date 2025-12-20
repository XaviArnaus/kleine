from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class MockedSerial(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(MockedSerial, self).init_pyxavi(config=config, params=params)
    
    def read_serial_data(self) -> dict:
        # Return mocked GPS data
        return {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timestamp": "12:34:56",
            "status": "A"
        }
    
    def get_gps_data(self) -> dict:
        return self.read_serial_data()