from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.objects.module_definitions import ModuleDefinitions

# from kleine.lib.accelerometer.accelerometer import Accelerometer
from kleine.lib.air_pressure.air_pressure import AirPressure
from kleine.lib.temperature.temperature import Temperature
from kleine.lib.ups.ups import Ups
from kleine.lib.gpio.gpio import Gpio
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.modules.display import Display
from kleine.lib.modules.display_power import DisplayPower
from kleine.lib.modules.display_temperature import DisplayTemperature
from kleine.lib.modules.display_info import DisplayInfo
from kleine.lib.utils.maintenance import Maintenance
from kleine.lib.utils.system import System

import time, math

class Main(PyXavi):

    STATUSBAR_SHOW_TIME: bool = True
    STATUSBAR_SHOW_TEMPERATURE: bool = True # Will be skipped in the temperature module
    STATUSBAR_SHOW_BATTERY: bool = True

    # accelerometer: Accelerometer = None
    air_pressure: AirPressure = None
    temperature: Temperature = None
    ups: Ups = None
    gpio: Gpio = None
    lcd: Lcd = None
    canvas: Canvas = None
    maintenance: Maintenance = None

    # All DisplayModules classes should have its own instance here
    display: Display = None
    display_temperature: DisplayTemperature = None
    display_info: DisplayInfo = None
    display_power: DisplayPower = None

    _last_processed_minute: int = -1
    scheduled_values: Dictionary = Dictionary({
        "temperature": 0,
        "humidity": 0,
        "air_pressure": 0,
    })

    # The index of the application modules is the order to cycle through them
    application_modules = [
        ModuleDefinitions.TEMPERATURE,
        ModuleDefinitions.ACCELEROMETER,
        ModuleDefinitions.INFO,
        ModuleDefinitions.SETTINGS,
        ModuleDefinitions.POWER,
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
        self._xlog.info("Initialising Display modules")
        self.display = Display(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd,
            "app_version": self._xparams.get("app_version")
        }))
        self.display_power = DisplayPower(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd
        }))
        self.display_temperature = DisplayTemperature(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd
        }))
        self.display_info = DisplayInfo(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd
        }))

        # Initialise the GPIO
        self._xlog.info("Initialising GPIO")
        self.gpio = Gpio(config=self._xconfig, params=self._xparams)

        # # Initialise the accelerometer
        # self._xlog.info("Initialising accelerometer.")
        # self.accelerometer = Accelerometer(config=self._xconfig, params=self._xparams)

        # Initialise the air pressure sensor
        self._xlog.info("Initialising air pressure sensor")
        self.air_pressure = AirPressure(config=self._xconfig, params=self._xparams)

        # Initialise the temperature sensor
        self._xlog.info("Initialising temperature sensor")
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

                    # Temperature module
                    if self.application_modules[selected_module] == ModuleDefinitions.TEMPERATURE:
                        self._xlog.debug("Running Temperature module")
                        self.display_temperature.module(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": False,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature"),
                            "humidity": self.scheduled_values.get("humidity"),
                            "air_pressure": self.scheduled_values.get("air_pressure")
                        }))
                    
                    # Accelerometer module
                    elif self.application_modules[selected_module] == ModuleDefinitions.ACCELEROMETER:
                        self._xlog.debug("Running Accelerometer module")
                        self.display.module_accelerometer(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature")
                        }))

                    # Power module
                    elif self.application_modules[selected_module] == ModuleDefinitions.POWER:
                        self._xlog.debug("Running Power module")
                        self.display_power.module(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature")
                        }))
                    
                    # Info module
                    elif self.application_modules[selected_module] == ModuleDefinitions.INFO:
                        self._xlog.debug("Running Info module")
                        self.display_info.module(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature"),
                            "os_info": System.get_os_info(),
                            "network_interface": System.get_default_network_interface(),
                            "wifi_network": System.get_connected_wifi_info()
                        }))
                    
                    # Settings module
                    elif self.application_modules[selected_module] == ModuleDefinitions.SETTINGS:
                        self._xlog.debug("Running Settings module")
                        self.display.module_settings(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature")
                        }))
                    
                    # Unknown module
                    else:
                        self._xlog.debug("Selected module " + self.application_modules[selected_module] + " not implemented yet.")
                        self.display.blank_screen(parameters=Dictionary({
                            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
                            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
                            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
                            "battery_percentage": self.scheduled_values.get("battery_percentage"),
                            "battery_is_charging": self.scheduled_values.get("battery_is_charging"),
                            "temperature": self.scheduled_values.get("temperature")
                        }))

                # self._xlog.debug("Test accelerometer...")
                # self.accelerometer.test()

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

                current_air_pressure = round(self.air_pressure.get_air_pressure(), 1)
                if current_air_pressure != self.scheduled_values.get("air_pressure", 0):
                    self.scheduled_values.set("air_pressure", current_air_pressure)
                    return_value = True

                if return_value:
                    self._xlog.info(f"Updated scheduled values: Temperature={self.scheduled_values.get('temperature')}°C, Humidity={self.scheduled_values.get('humidity')}%, Air Pressure={self.scheduled_values.get('air_pressure')} hPa")

            if self.STATUSBAR_SHOW_TIME:
                self._xlog.debug("Time change requires screen refresh.")
                return_value = True
            
            if self.STATUSBAR_SHOW_BATTERY:
                current_battery_percentage = math.ceil(self.ups.get_battery_percentage())
                if current_battery_percentage != self.scheduled_values.get("battery_percentage", 0):
                    self.scheduled_values.set("battery_percentage", current_battery_percentage)
                    return_value = True

                current_battery_is_charging = self.ups.is_charging()
                if current_battery_is_charging != self.scheduled_values.get("battery_is_charging", False):
                    self.scheduled_values.set("battery_is_charging", current_battery_is_charging)
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
