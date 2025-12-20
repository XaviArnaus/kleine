from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
import pynmea2, serial
from datetime import datetime, timedelta

class GpsSerial(PyXavi):

    SERIAL_PORT: str = "/dev/ttyS0"
    TIMEOUT_IN_SECS: int = 30

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(GpsSerial, self).init_pyxavi(config=config, params=params)
    
    def read_serial_data(self) -> dict:

        # The approach that we do is to read the serial data line by line
        # for some iterations and try to parse each line as an NMEA sentence.
        # When we have a valid sentence, we return it and finish.

        # We introduce a timeout mechanism to avoid infinite loops
        timeout_time = datetime.now() + timedelta(seconds=self.TIMEOUT_IN_SECS)
        sentence_is_valid = False
        while not sentence_is_valid and datetime.now() < timeout_time:

            port=self.SERIAL_PORT
            with serial.Serial(port, baudrate=9600, timeout=1) as ser:
                line = ser.readline().decode('ascii', errors='replace').strip()
                self._xlog.debug(f"Read line from GPS serial: {line}")
                try:
                    # Read the GPS Vendor PDF. We should be parsing all possible GPS Talker IDs!!
                    # if line[0:6]=="$GPRMC":
                        msg = pynmea2.parse(line)
                        self._xlog.debug(f"Parsed NMEA sentence: {msg}")
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            sentence_is_valid = True
                            return {
                                "latitude": msg.latitude,
                                "longitude": msg.longitude,
                                # "timestamp": msg.timestamp,
                                # "status": msg.status
                            }
                except pynmea2.ParseError as e:
                    self._xlog.error(f"Failed to parse NMEA sentence: {e}")
                    continue
        
        if not sentence_is_valid:
            self._xlog.error("Timeout reached while reading GPS data from serial port")
            # return {
            #     "latitude": None,
            #     "longitude": None,
            #     "timestamp": None,
            #     "status": "V"  # V = Void (no valid data)
            # }
            return None
