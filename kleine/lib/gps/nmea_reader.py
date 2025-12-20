from pyxavi import Config, Dictionary, full_stack, dd
from kleine.lib.abstract.pyxavi import PyXavi

import serial
import time
import threading
import pynmea2
import queue
from logging import Logger

# https://github.com/Brinda-93/GNSS_NMEA/blob/main/gnss_reader.py

class NMEAReader(PyXavi):

    # ========= USER SETTINGS =========
    # SERIAL_PORT = '/dev/ttyUSB0'    # Change to your port (e.g., '/dev/ttyUSB0')
    SERIAL_PORT = "/dev/ttyS0"
    BAUD_RATE = 115200
    UPDATE_INTERVAL_MS = 1000   # e.g., 200ms = 5Hz
    USE_GPS = True
    USE_GLONASS = True
    USE_GALILEO = True
    USE_BEIDOU = True
    # =================================

    serial_device: serial.Serial = None
    output_queue: queue.Queue = None
    receiver_thread: threading.Thread = None

    cumulative_data = {
        # Incoming from GGA
        "latitude": None,
        "longitude": None,
        "direction_latitude": None,
        "direction_longitude": None,
        "interval": None,
        "altitude": None,
        "altitude_units": None,
        "timestamp": None,
        "status": None,
        # Unmerged from RMC
        "speed": None,
        "heading": None,
    }

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(NMEAReader, self).init_pyxavi(config=config, params=params)

        self.output_queue = params.get("output_queue", queue.Queue())
        # if self.output_queue is None:
        #     raise ValueError("An output_queue to deliver data is required")

        # Initialize serial connection
        try:
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
            self.receiver_thread = threading.Thread(target=self.read_nmea_loop, args=(
                self.serial_device, 
                config, 
                self._xlog,
                self.output_queue
            ))
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


    def read_nmea_loop(self, ser: serial.Serial, config: Config = None, xlog: Logger = None, output_queue: queue.Queue = None):
        xlog.debug(">>> Listening for NMEA data...\n")
        last_fix_time = None

        # with ser:
        with serial.Serial(NMEAReader.SERIAL_PORT, NMEAReader.BAUD_RATE, timeout=1) as ser:
            xlog.debug("Context Serial")
            while True:
                xlog.debug("Loop")
                try:
                    line = ser.readline().decode('ascii', errors='replace').strip()
                    xlog.debug(f"Line: {line}")
                    if not line.startswith("$"):
                        xlog.debug("Uselsess line")
                        continue

                    try:
                        msg = pynmea2.parse(line)

                        if isinstance(msg, pynmea2.types.talker.GGA):
                            fix_status = int(msg.gps_qual)
                            if fix_status > 0:  # Only show if there's a fix
                                current_time = time.time()
                                interval = (current_time - last_fix_time) if last_fix_time else 0
                                last_fix_time = current_time
                                xlog.info(f"[GGA] Fix: {fix_status} | Interval: {interval:.2f}s | Time: {msg.timestamp} | Lat: {msg.latitude} {msg.lat_dir} | Lon: {msg.longitude} {msg.lon_dir} | Alt: {msg.altitude} {msg.altitude_units}")
                                # Send data to output queue
                                nmea_data = {
                                    "latitude": round(msg.latitude, 6),
                                    "longitude": round(msg.longitude, 6),
                                    "direction_latitude": msg.lat_dir,
                                    "direction_longitude": msg.lon_dir,
                                    "interval": interval,
                                    "altitude": msg.altitude,
                                    "altitude_units": msg.altitude_units,
                                    "timestamp": msg.timestamp.isoformat(),
                                    "status": "A" if fix_status > 0 else "V",
                                }
                                output_queue.put(nmea_data)

                        elif isinstance(msg, pynmea2.types.talker.RMC):
                            if msg.status == 'A':  # A = Valid fix
                                current_time = time.time()
                                interval = (current_time - last_fix_time) if last_fix_time else 0
                                last_fix_time = current_time
                                xlog.info(f"[RMC] Interval: {interval:.2f}s | Time: {msg.timestamp} | Lat: {msg.latitude} | Lon: {msg.longitude} | Speed: {msg.spd_over_grnd} knots | Heading: {msg.true_course}°")
                                # Send data to output queue
                                nmea_data = {
                                    "latitude": round(msg.latitude, 6),
                                    "longitude": round(msg.longitude, 6),
                                    "speed": round(msg.spd_over_grnd, 6),
                                    "heading": round(msg.true_course, 6),
                                    "interval": interval,
                                    "timestamp": msg.timestamp.isoformat(),
                                    "status": msg.status,
                                }
                                output_queue.put(nmea_data)

                    except pynmea2.ParseError as e:
                        xlog.error(f"Failed to parse NMEA sentence: {e}")
                        # continue

                except KeyboardInterrupt:
                    xlog.warning("Stopped.")
                    break

                except Exception as e:
                    xlog.error(f"Error in the GPS thread loop: {e}")
                    xlog.debug(full_stack())

    def close(self):
        while self.output_queue.get():
            self._xlog.debug("hey")
            self.output_queue.task_done()

    def get_gps_data(self) -> dict:
        self._xlog.debug("Consuming the NMEA messages queue comming from the reading thread")
        count = self.consume_nmea_data()
        self._xlog.debug(f"Return the last compiled state from {count} messages")
        return self.cumulative_data

    def consume_nmea_data(self) -> int:
        """
        Consume data from the output queue.
        Be aware that this actually makes `interval` and `speed` kinda useless.
        Also, technically it may never end.
        """
        count = 0
        while not self.output_queue.empty():
            nmea_data: dict = self.output_queue.get()  # wait for data
            self.cumulative_data = {
                **nmea_data,
                **self.cumulative_data
            }
            count += 1
            self.output_queue.task_done()
        return count