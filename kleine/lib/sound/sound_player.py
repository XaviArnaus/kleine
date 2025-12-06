from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.abstract.xobject import xObject
from pyxavi import Config, Dictionary

import sounddevice as sd

class SoundPlayer(PyXavi):
    """
    Sound management class using sounddevice

    This class provides methods to load, play, and manage sounds using the sounddevice library.
    If 
    """

    # Defining a default sound device configuration
    DEVICE = Dictionary({
        "id": 0,
        "name": "wm8960soundcard",
        "channels": 2,
        "sample_rate": 44100,
        "dtype": "int16",
        "blocksize": 1024
    })

    driver: sd.OutputStream = None

    loaded_sound: dict = {}

    _is_playing: dict = {}

    def __init__(self, config: Config, params: Dictionary = Dictionary({})):
        super(SoundPlayer, self).init_pyxavi(config=config, params=params)

        self.DEVICE.merge(params.get("device", Dictionary({})))
        self.driver = sd.OutputStream(
            device=self.DEVICE.get("id"),
            channels=self.DEVICE.get("channels"),
            samplerate=self.DEVICE.get("sample_rate"),
            dtype=self.DEVICE.get("dtype"),
            blocksize=self.DEVICE.get("blocksize")
        )

    def load_mp3(self, mp3_file: str, name: str = None):
        """
        Load and prepare MP3 file for playback

        mp3_file: Path to the MP3 file
        name: Optional name to reference the loaded sound

        if name is None, it will be stored as "default",
        so, all further loads without a name overwrite the default sound.
        """
        if name is None:
            name = "default"
        
        import numpy as np
        from pydub import AudioSegment

        # Load MP3 and convert to PCM (NumPy array)
        audio_data = AudioSegment.from_mp3(mp3_file)
        # Get sample rate and data (convert to float32 for sounddevice)
        frame_rate = audio_data.frame_rate
        audio_np = np.array(audio_data.get_array_of_samples()).astype(np.float32)
        # Normalize if needed (good practice for float data)
        audio_np = audio_np / np.max(np.abs(audio_np))

        self.loaded_sound[name] = {
            "data": audio_np,
            "frame_rate": frame_rate
        }
    
    def is_playing(self, name: str = None) -> bool:
        """
        Check if a sound is currently playing
        """
        if name is None:
            name = "default"

        return self._is_playing.get(name, False)
    
    def play(self, name: str = None, interrupt_if_playing: bool = True):
        """
        Play loaded sound by name
        """
        if name is None:
            name = "default"

        if name not in self.loaded_sound:
            self._xlog.error(f"Sound {name} not loaded.")
            return
        
        # Stop if already playing, or ignore depending on the flag.
        if self.is_playing(name=name):
            if interrupt_if_playing:
                self.stop(name=name)
            else:
                return

        # Play sound
        self._is_playing[name] = True
        sd.play(
            self.loaded_sound[name]["data"],
            samplerate=self.loaded_sound[name]["frame_rate"],
            blocking=True)
        # sd.wait()
        self._is_playing[name] = False
    
    def stop(self, name: str = None):
        """
        Stop playing sound by name
        """
        if name is None:
            name = "default"

        sd.stop()
        self._is_playing[name] = False
    
    def close(self):
        """
        Close the sound device and empties the loaded data
        """
        self.driver.close()
        self.loaded_sound = None

