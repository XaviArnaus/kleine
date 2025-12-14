from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.objects.module_definitions import ModuleDefinitions

# from kleine.lib.accelerometer.accelerometer import Accelerometer
# from kleine.lib.air_pressure.air_pressure import AirPressure
from kleine.lib.temperature.temperature import Temperature
from kleine.lib.ups.ups import Ups
from kleine.lib.gpio.gpio import Gpio
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.modules.display import Display
from kleine.lib.utils.maintenance import Maintenance

import time

class Main(PyXavi):

    STATUSBAR_SHOW_TIME: bool = True
    STATUSBAR_SHOW_TEMPERATURE: bool = True # Will be skipped in the temperature module

    # accelerometer: Accelerometer = None
    # air_pressure: AirPressure = None
    # temperature: Temperature = None
    ups: Ups = None
    gpio: Gpio = None
    lcd: Lcd = None
    canvas: Canvas = None
    display: Display = None
    maintenance: Maintenance = None

    _last_processed_minute: int = -1
    scheduled_values: Dictionary = Dictionary({
        "temperature": 0,
        "humidity": 0,
        "air_pressure": 0,
    })

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

        # Initialise the temperature sensor
        self._xlog.info("Initialising temperature sensor.")
        self.temperature = Temperature(config=self._xconfig, params=self._xparams)

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
        time.sleep(3)

        # We have a pair of physical buttons.
        # The yellow button is for "select" and the green button is for "enter".
        # The app rotates through different tests or displays on yellow button press like token ring.
        # The yellow button press moves to the next test/display.
        # The green button press performs an action on the current test/display.
        selected_module = -1

        try:
            while True:

                # Check the things to do every minute
                should_refresh = self.do_every_minute_tasks() or selected_module == -1

                # Handle module selection by pressing the Yellow button or at startup
                if self.gpio.is_button_pressed("yellow") or selected_module == -1:
                    selected_module += 1
                    if selected_module >= len(self.application_modules):
                        selected_module = 0
                    self._xlog.info("Yellow button pressed - moving to next module: " + self.application_modules[selected_module])
                    time.sleep(0.5) # Debounce delay
                    should_refresh = True
                
                # Run the selected module.
                # Must happen after the button press handling to avoid skipping modules.
                if should_refresh:
                    if self.application_modules[selected_module] == ModuleDefinitions.TEMPERATURE:
                        self._xlog.debug("Running Temperature module")
                        self.display.module_temperature(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": False,
                            "temperature": self.scheduled_values.get("temperature")
                        }))
                    else:
                        self._xlog.debug("Selected module " + self.application_modules[selected_module] + " not implemented yet.")
                        self.display.blank_screen(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "temperature": self.scheduled_values.get("temperature")
                        }))

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

    def do_every_minute_tasks(self) -> bool:
        """
        Tasks that need to be done every minute.
        Returns True if refreshing the screen is needed, False otherwise.
        """
        current_minute = time.localtime().tm_min
        if current_minute != self._last_processed_minute:
            self._last_processed_minute = current_minute
            self._xlog.debug("🕐 New minute detected: " + str(current_minute) + ". Running every-minute tasks.")

            # By default we do not need to refresh the screen
            return_value = False

            # Get temperature and humidity from the temperature sensor
            if self.STATUSBAR_SHOW_TEMPERATURE:
                current_temperature = round(self.temperature.get_temperature(), 1)
                if current_temperature != self.scheduled_values.get("temperature", 0):
                    self.scheduled_values.set("temperature", current_temperature)
                    return_value = True

                current_humidity = round(self.temperature.get_humidity(), 1)
                if current_humidity != self.scheduled_values.get("humidity", 0):
                    self.scheduled_values.set("humidity", current_humidity)
                    return_value = True

                if return_value:
                    self._xlog.info(f"Updated scheduled values: Temperature={self.scheduled_values.get('temperature')}°C, Humidity={self.scheduled_values.get('humidity')}%")

            if self.STATUSBAR_SHOW_TIME:
                self._xlog.debug("Time change requires screen refresh.")
                return_value = True

            # We have a status change
            return return_value
        
        # No change in minute, no tasks to do
        return False

    def close_nicely(self):
        self._xlog.debug("Closing nicely")

        # Clean the canvas
        if self.display is not None:
            self._xlog.debug("Cleaning display canvas")
            self.display.blank_screen(parameters=Dictionary({
                "statusbar_active": False
            }))

        # Close the LCD
        if self.lcd is not None:
            self._xlog.debug("Closing LCD")
            self.lcd.close()
        
        # Close the UPS
        if self.ups is not None:
            self._xlog.debug("Closing UPS")
            self.ups.close()
