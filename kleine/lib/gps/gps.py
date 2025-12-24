from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.gps.mocked_serial import MockedSerial

import os
import simplekml

class GPS(PyXavi):

    DEFAULT_MAIN_STORAGE = "storage"
    DEFAULT_TRACK_LOCATION = "tracks"
    MAX_TRACK_POINTS = 2000

    driver: MockedSerial = None
    track_storage = None
    kml_handler: simplekml.Kml = None
    track_handler: simplekml.GxTrack = None
    track_name: str = None
    current_track_point_counter: int = 0
    track_split_suffix_counter: int = 0

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(GPS, self).init_pyxavi(config=config, params=params)

        if self._xconfig.get("gps.mock", True):
            self.driver = MockedSerial(config=config, params=params)
        else:
            from kleine.lib.gps.nmea_reader import NMEAReader
            self.driver = NMEAReader(config=config, params=params)

        self.track_storage = os.path.join(
            self._xconfig.get("storage.path", self.DEFAULT_MAIN_STORAGE),
            self._xconfig.get("gps.track_storage", self.DEFAULT_TRACK_LOCATION)
        )
        if not os.path.exists(self.track_storage):
            os.makedirs(self.track_storage)

    def close(self):
        self.driver.close()

    def get_position(self) -> dict | None:
        data = self.driver.get_gps_data()
        # dd({
        #     # Incoming from GGA
        #     "latitude": data.get("latitude"),
        #     "longitude": data.get("longitude"),
        #     "direction_latitude": data.get("direction_latitude"),
        #     "direction_longitude": data.get("direction_longitude"),
        #     "interval": data.get("interval"),
        #     "altitude": data.get("altitude"),
        #     "altitude_units": data.get("altitude_units"),
        #     "timestamp": data.get("timestamp"),
        #     "status": data.get("status"),
        #     "signal_quality": data.get("signal_quality"),
        #     # Unmerged from RMC
        #     "speed": data.get("speed"),
        #     "heading": data.get("heading"),
        # })
        return data

    def start_recording_track(self, track_name: str = None):
        if self.kml_handler is not None:
            self._xlog.warning("KML recording is already started, will not overwrite.")
            return

        self.track_name = track_name if track_name is not None else self._generate_new_track_name()
        self.kml_handler = simplekml.Kml()
        self.track_handler = self.kml_handler.newgxtrack(
            name=self.track_name,
            altitudemode=simplekml.AltitudeMode.clamptoground)
        self.track_handler.style.linestyle.width = 3
        self.track_handler.style.linestyle.color = simplekml.Color.red
        self._xlog.info(f"📍 Start recording a track: {self.track_name}")

    def record_track_steppoint(self, latitude: float, longitude: float, altitude: float = 0.0, timestamp: str = ""):
        if self.kml_handler is None:
            self._xlog.warning("KML recording was not started, cannot record point.")
            return

        self.track_handler.newgxcoord(coord=[(longitude, latitude, altitude)])
        self.track_handler.newwhen(when=[timestamp])
        self.current_track_point_counter += 1
        self._xlog.debug(f"📍 Recorded KML point {self.current_track_point_counter}: lat={latitude}, lon={longitude}, alt={altitude}, timestamp={timestamp}")

    def split_recording_track_if_too_many_points(self) -> bool:
        if self.current_track_point_counter >= self.MAX_TRACK_POINTS:
            self._xlog.info("📍 Maximum track points reached, splitting track.")

            track_name = self._generate_split_track_name(base_track_name=self.track_name,
                                                             suffix_counter=self.track_split_suffix_counter)
            self.track_split_suffix_counter += 1

            # We stop the current recording adding a suffix to the track name that will be used as filename
            self.stop_recording_track(track_name=track_name)
            # We start a new recording with the original track name
            self.start_recording_track(track_name=self.track_name)
            return True
        return False

    def stop_recording_track(self, track_name: str = None) -> bool:
        if self.kml_handler is None:
            self._xlog.warning("KML recording was not started, cannot stop recording.")
            return False

        track_name = track_name if track_name is not None else self.track_name
        if self.track_split_suffix_counter > 0:
            track_name = self._generate_split_track_name(
                base_track_name=self.track_name,
                suffix_counter=self.track_split_suffix_counter)
        filename = self._generate_new_track_filename(track_name=track_name)
        filepath = os.path.join(self.track_storage, filename)
        self.kml_handler.save(filepath)
        self.kml_handler = None
        self.track_handler = None
        self._xlog.info(f"📍 KML track saved to {filepath}")
        return True
    
    def _generate_new_track_name(self) -> str:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"track_{timestamp}"
    
    def _generate_split_track_name(self, base_track_name: str, suffix_counter: int) -> str:
        return f"{base_track_name}_part_{suffix_counter}"

    def _generate_new_track_filename(self, track_name: str = None) -> str:
        if track_name is None:
            track_name = self._generate_new_track_name()
        return f"{track_name}.kml"