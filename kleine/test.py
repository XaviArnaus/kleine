from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from definitions import ROOT_DIR

from time import sleep
from PIL import Image
import sys
import os
import pygame  # Import pygame
import pygame._sdl2.audio as sdl2_audio
import subprocess
from kleine.lib.Whisplay.WhisPlay import WhisPlayBoard


class Test(PyXavi):

    CARD_ID = 0
    CARD_NAME = 'wm8960soundcard'
    CONTROL_NAME = 'Speaker'
    # DEVICE_ARG = f'hw:{CARD_NAME}'
    # DEVICE_ARG = f'hw:{CARD_ID},0'
    # DEVICE_ARG = f'{CARD_ID}'
    DEVICE_ARG = f'{CARD_NAME}'    

    VENDOR_PATH =  f"{ROOT_DIR}/vendor/pisugar/example/"

    board: WhisPlayBoard

    global_image_data = None
    image_filepath = None

    sound = None
    playing = False

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Test, self).init_pyxavi(config=config, params=params)

        self.board = WhisPlayBoard()
        self.board.set_backlight(50)
        # Initialize pygame mixer
        pygame.mixer.init(devicename=self.CARD_NAME, frequency=44100, size=-16, channels=2, buffer=512)
        self.sound = None  # Global sound variable
        self.playing = False  # Global variable to track if sound is playing

    @staticmethod
    def get_devices(capture_devices: bool = False) -> tuple[str, ...]:
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
        if init_by_me:
            pygame.mixer.quit()
        return devices

    def run(self):

        self._xlog.info("🚀 Starting Kleine TEST run...")

        # Register button event
        self.board.on_button_press(self.on_button_pressed)

        # --- Initial Image Loading ---
        # Load the image once at the beginning of the script
        self.image_filepath = self.VENDOR_PATH + "test.png"
        try:
            self.global_image_data = self.load_jpg_as_rgb565(
                self.image_filepath,
                self.board.LCD_WIDTH,
                self.board.LCD_HEIGHT)
            self.board.draw_image(0, 0, self.board.LCD_WIDTH, self.board.LCD_HEIGHT, self.global_image_data)
            print(
                f"Image {os.path.basename(self.image_filepath)} loaded and displayed initially.")
        except Exception as e:
            print(f"Failed to load initial image from {self.image_filepath}: {e}")

        # Load the sound
        self.sound_filepath = self.VENDOR_PATH + "test.mp3"
        try:
            self.sound = pygame.mixer.Sound(self.sound_filepath)
            print(f"Sound {os.path.basename(self.sound_filepath)} loaded successfully.")
            self.set_wm8960_volume_stable("121")  # Set volume to 121（74）
        except Exception as e:
            print(f"Failed to load sound from {self.sound_filepath}: {e}")
            self.sound = None

        try:
            print("Waiting for button press (Press Ctrl+C to exit)...")
            while True:
                # Check if the sound has finished playing and update the 'playing' flag
                if self.playing and not pygame.mixer.get_busy():
                    self.playing = False
                    # print("Sound finished playing.") # Optional print
                sleep(0.1)

        except KeyboardInterrupt:
            print("Exiting program...")

        finally:
            self.board.cleanup()
            pygame.mixer.quit()  # Quit the mixer

        # End copy from example

    def set_wm8960_volume_stable(self, volume_level: str):
        """
        Sets the 'Speaker' volume for the wm8960 sound card using the amixer command.

        Args:
            volume_level (str): The desired volume value, e.g., '90%' or '121'.
        """

        command = [
            'amixer',
            '-D', self.DEVICE_ARG,
            'sset',
            self.CONTROL_NAME,
            volume_level
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)

            print(
                f"INFO: Successfully set '{self.CONTROL_NAME}' volume to {volume_level} on card '{self.CARD_NAME}'.")

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to execute amixer.", file=sys.stderr)
            print(f"Command: {' '.join(command)}", file=sys.stderr)
            print(f"Return Code: {e.returncode}", file=sys.stderr)
            print(f"Error Output:\n{e.stderr}", file=sys.stderr)
        except FileNotFoundError:
            print("ERROR: 'amixer' command not found. Ensure it is installed and in PATH.", file=sys.stderr)


    def load_jpg_as_rgb565(self, filepath, screen_width, screen_height):
        img = Image.open(filepath).convert('RGB')
        original_width, original_height = img.size

        aspect_ratio = original_width / original_height
        screen_aspect_ratio = screen_width / screen_height

        if aspect_ratio > screen_aspect_ratio:
            # Original image is wider, scale based on screen height
            new_height = screen_height
            new_width = int(new_height * aspect_ratio)
            resized_img = img.resize((new_width, new_height))
            # Calculate horizontal offset to center the image
            offset_x = (new_width - screen_width) // 2
            # Crop the image to fit screen width
            cropped_img = resized_img.crop(
                (offset_x, 0, offset_x + screen_width, screen_height))
        else:
            # Original image is taller or has the same aspect ratio, scale based on screen width
            new_width = screen_width
            new_height = int(new_width / aspect_ratio)
            resized_img = img.resize((new_width, new_height))
            # Calculate vertical offset to center the image
            offset_y = (new_height - screen_height) // 2
            # Crop the image to fit screen height
            cropped_img = resized_img.crop(
                (0, offset_y, screen_width, offset_y + screen_height))

        pixel_data = []
        for y in range(screen_height):
            for x in range(screen_width):
                r, g, b = cropped_img.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixel_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])

        return pixel_data

    # Button callback function


    def on_button_pressed(self):
        print("Button pressed!")

        # --- MODIFICATION START: Play sound BEFORE screen changes ---
        if self.sound:
            if self.playing:
                self.sound.stop()  # Stop the current sound if it's playing
                print("Stopping current sound...")
            channel = self.sound.play()  # Play the sound from the beginning
            print("Playing sound concurrently with display changes...")
            self.playing = True  # Set the playing flag
            print("Sound is playing")
            while channel.get_busy():
                print(".", end=" ")
                pygame.time.delay(100)
            print("\nSound has finished playing.")
        else:
            print("Sound not loaded.")
        # --- MODIFICATION END ---

        # Display red filled screen
        self.board.fill_screen(0xF800)  # Red RGB565
        self.board.set_rgb(255, 0, 0)
        sleep(0.5)

        # Display green filled screen
        self.board.fill_screen(0x07E0)  # Green RGB565
        self.board.set_rgb(0, 255, 0)
        sleep(0.5)

        # Display blue filled screen
        self.board.fill_screen(0x001F)  # Blue RGB565
        self.board.set_rgb(0, 0, 255)
        sleep(0.5)

        # Display the image using the globally stored data
        if self.global_image_data is not None:
            self.board.draw_image(0, 0, self.board.LCD_WIDTH,
                            self.board.LCD_HEIGHT, self.global_image_data)
            print(
                f"Image {os.path.basename(self.image_filepath)} displayed successfully from memory.")
        else:
            print("Image data not loaded yet. This should not happen after initial load.")
