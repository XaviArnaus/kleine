from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.objects.module_definitions import ModuleDefinitions

# from kleine.lib.accelerometer.accelerometer import Accelerometer
# from kleine.lib.air_pressure.air_pressure import AirPressure
# from kleine.lib.temperature.temperature import Temperature
from kleine.lib.ups.ups import Ups
from kleine.lib.gpio.gpio import Gpio
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.modules.display import Display
from kleine.lib.utils.maintenance import Maintenance

import time

class Main(PyXavi):

    # accelerometer: Accelerometer = None
    # air_pressure: AirPressure = None
    # temperature: Temperature = None
    ups: Ups = None
    gpio: Gpio = None
    lcd: Lcd = None
    canvas: Canvas = None
    display: Display = None
    maintenance: Maintenance = None

    # The index of the application modules is the order to cycle through them
    application_modules = [
        ModuleDefinitions.TEMPERATURE,
        ModuleDefinitions.AIR_PRESSURE,
        ModuleDefinitions.ACCELEROMETER,
        ModuleDefinitions.POWER,
        ModuleDefinitions.INFO,
        ModuleDefinitions.SETTINGS
    ]

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

        ## Why so many classes related to the display?
        # Lcd: is the hardware driver for the LCD screen. It wraps the ST7789 driver and the final drawing to it.
        # Canvas: is the drawing surface where we create images to be sent to the LCD.
        # Display: is the module that uses the Canvas to draw things like text, shapes, images, etc.

        # Initialise the LCD display
        self._xlog.info("Initialising LCD device")
        self.lcd = Lcd(config=self._xconfig, params=self._xparams)

        # Initialise the Canvas
        self._xlog.info("Initialising Canvas")
        self.canvas = Canvas(config=self._xconfig, params=Dictionary({
            "screen_size": self.lcd.get_screen_size(),
            "device_config_prefix": "lcd",
            # "color_mode" and "font_file" could be added here if needed
        }))

        # Initialise the Display module
        self._xlog.info("Initialising Display module")
        self.display = Display(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd,
            "app_version": self._xparams.get("app_version")
        }))

        # Initialise the GPIO
        self._xlog.info("Initialising GPIO")
        self.gpio = Gpio(config=self._xconfig, params=self._xparams)

        # # Initialise the accelerometer
        # self._xlog.info("Initialising accelerometer.")
        # self.accelerometer = Accelerometer(config=self._xconfig, params=self._xparams)

        # # Initialise the air pressure sensor
        # self._xlog.info("Initialising air pressure sensor.")
        # self.air_pressure = AirPressure(config=self._xconfig, params=self._xparams)

        # # Initialise the temperature sensor
        # self._xlog.info("Initialising temperature sensor.")
        # self.temperature = Temperature(config=self._xconfig, params=self._xparams)

        # Initialise the UPS
        self._xlog.info("Initialising UPS")
        self.ups = Ups(config=self._xconfig, params=self._xparams)

        # Initialise the Maintenance utility
        self._xlog.info("Initialising Maintenance utility")
        self.maintenance = Maintenance(config=self._xconfig, params=Dictionary({
            "storage_path": self._xparams.get("storage_path", "storage/"),
            "mocked_paths": [self._xconfig.get("storage.mocked_files.lcd")]
        }))

    def run(self):

        self._xlog.info("🚀 Starting Kleine main run")

        # Clean previous mocked images
        self.maintenance.clean_previous_mocked_images()

        # Show startup splash screen
        self.display.startup_splash()
        time.sleep(2)

        # We have a pair of physical buttons.
        # The yellow button is for "select" and the green button is for "enter".
        # The app rotates through different tests or displays on yellow button press like token ring.
        # The yellow button press moves to the next test/display.
        # The green button press performs an action on the current test/display.
        selected_module = 0

        try:
            while True:

                # Handle module selection by pressing the Yellow button
                if self.gpio.is_yellow_button_pressed():
                    self._xlog.info("Yellow button pressed - moving to next module")
                    selected_module += 1
                    if selected_module >= len(self.application_modules):
                        selected_module = 0
                    time.sleep(0.5) # Debounce delay

                # # self.macros.startup_splash(display=self.eink)
                # self.lcd.test()
                # time.sleep(2)

                # self._xlog.debug("Test accelerometer...")
                # self.accelerometer.test()

                # self._xlog.debug("Test air pressure...")
                # self.air_pressure.test()

                # self._xlog.debug("Test temperature...")
                # self.temperature.test()

                # self._xlog.debug("Test UPS...")
                # self.ups.test()

        except Exception as e:
            self._xlog.error(f"Exception in main run: {e}")
        except KeyboardInterrupt:
            self._xlog.info("Control + C detected")

        # However it happened, just close nicely.
        self.close_nicely()
    
    def run_temperature_module(self):
        """
        Run the temperature module.

        It happens inside the main loop, so consider this as a one interation run.
        """
        pass
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely")

        # Close the LCD
        if self.lcd is not None:
            self._xlog.debug("Closing LCD")
            self.lcd.close()
        
        # Close the UPS
        if self.ups is not None:
            self._xlog.debug("Closing UPS")
            self.ups.close()
