from pyxavi import Config, Dictionary, full_stack
from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.utils.calculations import Calculations
from kleine.lib.objects.gps_signal_quality import GPSSignalQuality

import serial
import time
import threading
import pynmea2
from logging import Logger

# https://github.com/Brinda-93/GNSS_NMEA/blob/main/gnss_reader.py

class NMEAReader(PyXavi):

    # ========= USER SETTINGS =========
    # SERIAL_PORT = '/dev/ttyUSB0'    # Change to your port (e.g., '/dev/ttyUSB0')
    SERIAL_PORT = "/dev/ttyS0"
    # BAUD_RATE = 115200
    BAUD_RATE = 9600
    UPDATE_INTERVAL_MS = 1000   # e.g., 200ms = 5Hz
    USE_GPS = True
    USE_GLONASS = True
    USE_GALILEO = True
    USE_BEIDOU = True
    # =================================

    ACTIVATE_LOGGING = False
    GOOD_SIGNAL_MIN_SATS = 6
    POOR_SIGNAL_MIN_SATS = 2

    thread_lock: threading.Lock = None
    receiver_thread: threading.Thread = None
    loop_is_allowed = True

    cumulative_data = {
        # Inferred
        "interval": None,
        # Incoming from GGA, GLL, RMC
        "latitude": None,
        "longitude": None,
        "timestamp": None,
        "status": None,
        # Incoming from GGA, GLL
        "direction_latitude": None,
        "direction_longitude": None,
        # Incoming from GGA
        "altitude": None,
        "altitude_units": None,
        "signal_quality": 0,    # We start with 0 = no fix
        "num_sats": 0,  # Number of satellites used in fix
        # Incoming from RMC
        "speed": None,
        "heading": None,
    }

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(NMEAReader, self).init_pyxavi(config=config, params=params)

        self.thread_lock = threading.Lock()
        self.ACTIVATE_LOGGING = self._xconfig.get("gps.activate_logging", self.ACTIVATE_LOGGING)

        self.SERIAL_PORT = self._xconfig.get("gps.hardware.serial_port", self.SERIAL_PORT)
        self.BAUD_RATE = self._xconfig.get("gps.hardware.baud_rate", self.BAUD_RATE)
        self.UPDATE_INTERVAL_MS = self._xconfig.get("gps.hardware.update_interval_ms", self.UPDATE_INTERVAL_MS)
        self.USE_GPS = self._xconfig.get("gps.hardware.use_gps", self.USE_GPS)
        self.USE_GLONASS = self._xconfig.get("gps.hardware.use_glonass", self.USE_GLONASS)
        self.USE_GALILEO = self._xconfig.get("gps.hardware.use_galileo", self.USE_GALILEO)
        self.USE_BEIDOU = self._xconfig.get("gps.hardware.use_beidou", self.USE_BEIDOU)
        self._xlog.info(f"Initializing NMEA Reader with: port [{self.SERIAL_PORT}], baud rate [{self.BAUD_RATE}], update interval [{self.UPDATE_INTERVAL_MS}], use GPS [{self.USE_GPS}], use GLONASS [{self.USE_GLONASS}], use Galileo [{self.USE_GALILEO}], use BeiDou [{self.USE_BEIDOU}]")

        # Configure the device
        try:
            # with serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1) as ser:
            # self.serial_device = serial.Serial(NMEAReader.SERIAL_PORT, NMEAReader.BAUD_RATE, timeout=1)
            # time.sleep(2)  # Wait for module to initialize

            # self._xlog.debug(">>> Configuring GNSS systems...")
            # self.configure_gnss_systems(self.serial_device)

            # self._xlog.debug(">>> Setting output interval...")
            # self.configure_update_rate(self.serial_device, NMEAReader.UPDATE_INTERVAL_MS)

            # self._xlog.debug(">>> Enabling NMEA messages...")
            # self.configure_nmea_output(self.serial_device)

            # self._xlog.debug(">>> Saving configuration...")
            # self.save_configuration(self.serial_device)

            self._xlog.debug(">>> Configuration done. Starting data read...\n")
            self.receiver_thread = threading.Thread(target=self.read_nmea_loop)
            self.receiver_thread.start()
        except serial.SerialException as e:
            self._xlog.error(f"Serial error: {e}")
            self._xlog.debug(full_stack())

    def calculate_checksum(self, nmea_str):
        checksum = 0
        for char in nmea_str:
            checksum ^= ord(char)
        return f"{checksum:02X}"

    def send_command(self, serial_port, base_command):
        nmea_body = base_command.strip().lstrip('$')
        checksum = self.calculate_checksum(nmea_body)
        full_command = f"${nmea_body}*{checksum}\r\n"
        serial_port.write(full_command.encode('ascii'))
        self._xlog.debug(f">> {full_command.strip()}")

    def configure_gnss_systems(self, ser):
        mode = 1  # enable/disable each individually
        gps = int(self.USE_GPS)
        glonass = int(self.USE_GLONASS)
        galileo = int(self.USE_GALILEO)
        beidou = int(self.USE_BEIDOU)
        # Format: $PQGNSS,<mode>,<gps>,<glonass>,<galileo>,<beidou>,<reserved>
        base_cmd = f"PQGNSS,{mode},{gps},{glonass},{galileo},{beidou},0"
        self.send_command(ser, base_cmd)


    def configure_update_rate(self, ser, interval_ms):
        interval_ms = max(200, interval_ms)  # minimum allowed by many modules
        rate_hz = int(1000 / interval_ms)
        base_cmd = f"PQTMCFGPMODE,{interval_ms}"
        self.send_command(ser, base_cmd)

        # Also try standard MTK-style command if your module supports it
        gga_rate = 1
        gsv_rate = 0
        gsa_rate = 0
        rmc_rate = 1
        vtg_rate = 0
        zda_rate = 0

        # Example: Set all sentence rates to 1 (1 Hz)
        self.send_command(ser, "PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        self.send_command(ser, f"PMTK220,{interval_ms}")  # Output interval in ms

    def configure_nmea_output(self, ser):
        self.send_command(ser, "PQTMCFGMSG,RMC,1")  # Enable RMC every fix
        self.send_command(ser, "PQTMCFGMSG,GGA,1")  # Enable GGA every fix

    def save_configuration(self, ser):
        self.send_command(ser, "PQTMSAVEPAR")


    def read_nmea_loop(self):

        last_fix_time = None

        with serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1) as ser:
            while True:
                # Control if we want to quit the loop
                if not self.loop_is_allowed:
                    if self.ACTIVATE_LOGGING:
                        self._xlog.debug("Loop not allowed, exiting it.")
                    break
                
                try:
                    # Now, pick the next sentence
                    line = ser.readline().decode('ascii', errors='replace').strip()
                    if self.ACTIVATE_LOGGING:
                        self._xlog.debug(line)

                    # Ignore what does not contain data
                    if not line.startswith("$"):
                        if self.ACTIVATE_LOGGING:
                            self._xlog.debug(f"🔵 Line does not start with $,  ignoring.")
                        continue

                    # Parse the sentence
                    msg = pynmea2.parse(line)
                    if self.ACTIVATE_LOGGING:
                        self._xlog.debug(msg)

                    if isinstance(msg, pynmea2.types.talker.GGA):
                        if msg.gps_qual is not None and msg.num_sats is not None:
                            self.cumulative_data["signal_quality"] = self.get_signal_quality(int(msg.gps_qual), int(msg.num_sats))
                            self.cumulative_data["num_sats"] = int(msg.num_sats)
                            if self.ACTIVATE_LOGGING:
                                self._xlog.debug(f"📶 Updating signal quality based on GGA data: {self.cumulative_data['signal_quality']}, {self.cumulative_data['num_sats']} sats")
                        # GPS Fix status codes, 0 is invalid, bigger is more accuracy
                        # 0: Fix not valid
                        # 1: GPS fix
                        # 2: Differential GPS fix (DGNSS), SBAS, OmniSTAR VBS, Beacon, RTX in GVBS mode
                        # 3: Not applicable
                        # 4: RTK Fixed, xFill
                        # 5: RTK Float, OmniSTAR XP/HP, Location RTK, RTX
                        # 6: INS Dead reckoning
                        fix_status = int(msg.gps_qual)
                        if self.ACTIVATE_LOGGING:
                            icon = "🟢" if fix_status > 0 else "🔴"
                            self._xlog.debug(f"{icon} GGA with fix: {fix_status} ( > 0 is valid )")
                        if fix_status > 0:  # Only show if there's a fix
                            current_time = time.time()
                            interval = (current_time - last_fix_time) if last_fix_time else 0
                            last_fix_time = current_time
                            if self.ACTIVATE_LOGGING:
                                self._xlog.info(f"🟢 [GGA] Fix: {fix_status} | Interval: {interval:.2f}s | Time: {msg.timestamp} | Lat: {msg.latitude} {msg.lat_dir} | Lon: {msg.longitude} {msg.lon_dir} | Alt: {msg.altitude} {msg.altitude_units}")
                            # Send data to output queue
                            nmea_data = {
                                "latitude": round(msg.latitude, 6),
                                "longitude": round(msg.longitude, 6),
                                "direction_latitude": msg.lat_dir if hasattr(msg, "lat_dir") else None,
                                "direction_longitude": msg.lon_dir if hasattr(msg, "lon_dir") else None,
                                "interval": interval,
                                "altitude": msg.altitude if hasattr(msg, "altitude") else None,
                                "altitude_units": msg.altitude_units.lower() if hasattr(msg, "altitude_units") else None,
                                "timestamp": msg.timestamp if hasattr(msg, "timestamp") else None,
                                "status": "A" if fix_status > 0 else "V",
                            }
                            with self.thread_lock:
                                self.cumulative_data = {
                                    **self.cumulative_data,
                                    **nmea_data
                                }

                    elif isinstance(msg, pynmea2.types.talker.RMC):
                        if self.ACTIVATE_LOGGING:
                            icon = "🟢" if msg.status == 'A' else "🔴"
                            self._xlog.debug(f"{icon} RMC with status: {msg.status} ( A=valid, V=invalid )")
                        if msg.status == 'A':  # A = Valid fix
                            current_time = time.time()
                            interval = (current_time - last_fix_time) if last_fix_time else 0
                            last_fix_time = current_time
                            if self.ACTIVATE_LOGGING:
                                self._xlog.info(f"🟢 [RMC] Interval: {interval:.2f}s | Time: {msg.timestamp} | Lat: {msg.latitude} | Lon: {msg.longitude} | Speed: {msg.spd_over_grnd} knots | Heading: {msg.true_course}°")
                            # Send data to output queue
                            nmea_data = {
                                "latitude": round(msg.latitude, 6),
                                "longitude": round(msg.longitude, 6),
                                "speed": round(Calculations.knots_to_kmh(msg.spd_over_grnd), 3)  if hasattr(msg, "spd_over_grnd") and msg.spd_over_grnd is not None else None,
                                "heading": msg.true_course if hasattr(msg, "true_course") and msg.true_course is not None else None,
                                "interval": interval,
                                "timestamp": msg.timestamp if hasattr(msg, "timestamp") else None,
                                "status": msg.status if hasattr(msg, "status") else None,
                            }
                            with self.thread_lock:
                                self.cumulative_data = {
                                    **self.cumulative_data,
                                    **nmea_data
                                }
                    
                    elif isinstance(msg, pynmea2.types.talker.GLL):
                        if self.ACTIVATE_LOGGING:
                            icon = "🟢" if msg.status == 'A' else "🔴"
                            self._xlog.debug(f"{icon} GLL with status: {msg.status} ( A=valid, V=invalid )")
                        if msg.status == 'A':  # A = Valid fix
                            current_time = time.time()
                            interval = (current_time - last_fix_time) if last_fix_time else 0
                            last_fix_time = current_time
                            if self.ACTIVATE_LOGGING:
                                self._xlog.info(f"🟢 [GLL] Interval: {interval:.2f}s | Time: {msg.timestamp} | Lat: {msg.latitude} {msg.lat_dir} | Lon: {msg.longitude} {msg.lon_dir}")
                            # Send data to output queue
                            nmea_data = {
                                "latitude": round(msg.latitude, 6),
                                "longitude": round(msg.longitude, 6),
                                "direction_latitude": msg.lat_dir if hasattr(msg, "lat_dir") else None,
                                "direction_longitude": msg.lon_dir if hasattr(msg, "lon_dir") else None,
                                "interval": interval,
                                "timestamp": msg.timestamp if hasattr(msg, "timestamp") else None,
                                "status": msg.status if hasattr(msg, "status") else None,
                            }
                            with self.thread_lock:
                                self.cumulative_data = {
                                    **self.cumulative_data,
                                    **nmea_data
                                }

                    else:
                        if self.ACTIVATE_LOGGING:
                            self._xlog.debug("🟠 Not GGA, GLL or RMC, ignoring.")

                except pynmea2.ParseError as e:
                    self._xlog.error(f"Failed to parse NMEA sentence: {e}")

                except KeyboardInterrupt:
                    self._xlog.warning("Detected a Control + C inside the Thread")
                    break

                except Exception as e:
                    self._xlog.error(f"Error in the GPS thread loop: {e}")
                    self._xlog.debug(full_stack())

    def get_signal_quality(self, fix: int = None, number_of_satellites: int = None) -> int | None:
        if fix is None or number_of_satellites is None:
            return GPSSignalQuality.SIGNAL_UNKNOWN

        if fix > 0:
            if number_of_satellites >= self.GOOD_SIGNAL_MIN_SATS:
                return GPSSignalQuality.SIGNAL_GOOD
            elif number_of_satellites >= self.POOR_SIGNAL_MIN_SATS:
                return GPSSignalQuality.SIGNAL_WEAK
        return GPSSignalQuality.SIGNAL_POOR

    def close(self):
        self.loop_is_allowed = False
        self.receiver_thread.join()

    def get_gps_data(self) -> dict:
        with self.thread_lock:
            data = self.cumulative_data
        return data