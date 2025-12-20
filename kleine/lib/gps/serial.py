from pyxavi import Config, Dictionary, dd
from kleine.lib.abstract.pyxavi import PyXavi
import pynmea2, serial
from datetime import datetime, timedelta

class GpsSerial(PyXavi):
    """
    This is the first approach to read from the GPS
    It works, but it's pretty simple and did not develop further.
    It is not used. Please refer to the NMEAReader
    """

    SERIAL_PORT: str = "/dev/ttyS0"
    TIMEOUT_IN_SECS: int = 30

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(GpsSerial, self).init_pyxavi(config=config, params=params)
    
    def read_serial_data(self) -> dict:

        # Remember that we're already running inside a loop in main.py
        # So we just need to read once from serial and return the data if valid

        sentence_is_valid = False
        port=self.SERIAL_PORT
        with serial.Serial(port, baudrate=9600, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace').strip()
            self._xlog.debug(f"Read line from GPS serial: {line}")
            try:
                    msg = pynmea2.parse(line)
                    self._xlog.debug(f"Parsed NMEA sentence: {msg}")
                    if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                        sentence_is_valid = True
                        print(msg)
                        return {
                            "latitude": round(msg.latitude, 6),
                            "longitude": round(msg.longitude, 6),
                            "direction_latitude": msg.lat_dir if hasattr(msg, 'lat_dir') else None,
                            "direction_longitude": msg.lon_dir if hasattr(msg, 'lon_dir') else None,
                            "altitude": msg.altitude if hasattr(msg, 'altitude') else None,
                            "altitude_units": msg.altitude_units if hasattr(msg, 'altitude_units') else None,
                            "timestamp": msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else None,
                            "status": msg.status if hasattr(msg, 'status') else None,
                        }
                    else:
                        self._xlog.debug("NMEA sentence does not contain GPS position data")
            except pynmea2.ParseError as e:
                self._xlog.error(f"Failed to parse NMEA sentence: {e}")
                # continue
        
        if not sentence_is_valid:
            self._xlog.error("Timeout reached while reading GPS data from serial port")
            return None
