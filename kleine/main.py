from pyxavi import Config, Dictionary, full_stack
from kleine.lib.abstract.pyxavi import PyXavi

from kleine.lib.objects.module_definitions import ModuleDefinitions, PowerActions

from kleine.lib.accelerometer.accelerometer import Accelerometer
from kleine.lib.air_pressure.air_pressure import AirPressure
from kleine.lib.temperature.temperature import Temperature
from kleine.lib.ups.ups import Ups
from kleine.lib.gpio.gpio import Gpio
from kleine.lib.gps.gps import GPS

from kleine.lib.lcd.lcd import Lcd
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.modules.display import Display
from kleine.lib.modules.display_power import DisplayPower
from kleine.lib.modules.display_temperature import DisplayTemperature
from kleine.lib.modules.display_info import DisplayInfo
from kleine.lib.modules.display_accelerometer import DisplayAccelerometer
from kleine.lib.modules.display_gps import DisplayGPS

from kleine.lib.utils.maintenance import Maintenance
from kleine.lib.utils.system import System

import time, math

class Main(PyXavi):

    STATUSBAR_SHOW_TIME: bool = True
    STATUSBAR_SHOW_TEMPERATURE: bool = True # Will be skipped in the temperature module
    STATUSBAR_SHOW_BATTERY: bool = True

    SECONDS_TO_REACT_FOR_TASKS: int = 2

    # accelerometer: Accelerometer = None
    air_pressure: AirPressure = None
    temperature: Temperature = None
    ups: Ups = None
    gpio: Gpio = None
    gps: GPS = None
    lcd: Lcd = None
    canvas: Canvas = None
    maintenance: Maintenance = None

    # All DisplayModules classes should have its own instance here
    display: Display = None
    display_temperature: DisplayTemperature = None
    display_info: DisplayInfo = None
    display_power: DisplayPower = None
    display_accelerometer: DisplayAccelerometer = None

    _last_processed_minute: int = -1
    _last_processed_second: int = -1
    gathered_values: Dictionary = Dictionary({
        "temperature": 0,
        "humidity": 0,
        "air_pressure": 0,
        "acceleration": (0,0,0),
        "gyroscope": (0,0,0),
        "magnetometer": (0,0,0),
        "pitch_roll_yaw": (0.0,0.0,0.0),
        "gps": {
            "latitude": 0.0,
            "longitude": 0.0,
            "direction_latitude": None,
            "direction_longitude": None,
            "altitude": None,
            "altitude_units": None,
            "timestamp": None,
            "status": None,
        }
    })

    # The index of the application modules is the order to cycle through them
    application_modules = [
        ModuleDefinitions.GPS,
        ModuleDefinitions.TEMPERATURE,
        ModuleDefinitions.ACCELEROMETER,
        # ModuleDefinitions.GPS,
        ModuleDefinitions.INFO,
        # ModuleDefinitions.SETTINGS,
        ModuleDefinitions.POWER,
    ]

    # Options tree for each module.
    # The index is the order of the options in the module.
    options_tree = {
        ModuleDefinitions.POWER: [
            PowerActions.POWER_SHUTDOWN,
            PowerActions.POWER_REBOOT,
            PowerActions.POWER_UPDATE_RESTART,
        ],
    }

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

        ## Why so many classes related to the display?
        # Lcd: is the hardware driver for the LCD screen. It wraps the ST7789 driver and the final drawing to it.
        # Canvas: is the drawing surface where we create images to be sent to the LCD.
        # Display: is the module that uses the Canvas to draw things like text, shapes, images, etc.
        # DisplayWhatever: are specific modules that use Display to show specific information.

        # Initialize some vars from the config or the state
        seconds = self._xconfig.get("scheduler.update_interval", self.SECONDS_TO_REACT_FOR_TASKS)
        if seconds >= 1 and seconds <= 60:
            self.SECONDS_TO_REACT_FOR_TASKS = seconds

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
        self.display_accelerometer = DisplayAccelerometer(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd
        }))
        self.display_gps = DisplayGPS(config=self._xconfig, params=Dictionary({
            "canvas": self.canvas,
            "device": self.lcd
        }))

        # Initialise the GPIO
        self._xlog.info("Initialising GPIO")
        self.gpio = Gpio(config=self._xconfig, params=self._xparams)

        # Initialise the GPS
        self._xlog.info("Initialising GPS")
        self.gps = GPS(config=self._xconfig, params=self._xparams)

        # # Initialise the accelerometer
        self._xlog.info("Initialising accelerometer.")
        self.accelerometer = Accelerometer(config=self._xconfig, params=self._xparams)

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

        # We have 3 physical buttons.
        # - The yellow button is for "menu select"
        # - The blue button is for "option select"
        # - The green button is for "enter".
        # The app rotates through different tests or displays on yellow button press like token ring.
        # The yellow button press moves to the next test/display.
        # The blue button press selects an option in the current test/display.
        # The green button press performs an action on the current test/display.
        selected_module = -1
        selected_option_in_module = -1
        modal_message = ""
        modal_wait = False
        refresh_again = False

        try:
            while True:

                # Accumulate the Should Refresh flag along the actions
                should_refresh = refresh_again or selected_module == -1

                 # The refresh flag is set to False after each check
                # It comes from the previous loop iteration, in case we showed a modal message
                refresh_again = False

                # Check the things to do every minute
                should_refresh = self.do_every_minute_tasks() or should_refresh

                # Check the things to do every given seconds
                should_refresh = self.do_every_seconds_tasks(selected_module) or should_refresh

                # Check real-time tasks
                should_refresh = self.do_real_time_tasks(selected_module) or should_refresh

                # Handle module selection by pressing the Yellow button or at startup
                if self.gpio.is_button_pressed("yellow") or selected_module == -1:
                    selected_module += 1
                    if selected_module >= len(self.application_modules):
                        selected_module = 0
                    
                    self._xlog.info("Yellow button pressed - moving to next module: " + 
                                    self.application_modules[selected_module])
                    # Reset option selection when changing module
                    selected_option_in_module = -1
                    time.sleep(0.2) # Debounce delay
                    should_refresh = True
                
                # Handle option selection in the current module by pressing the Blue button
                if self.gpio.is_button_pressed("blue"):
                    if self.application_modules[selected_module] in self.options_tree:
                        selected_option_in_module += 1
                        options_in_current_module = self.options_tree[self.application_modules[selected_module]]
                        if selected_option_in_module >= len(options_in_current_module):
                            selected_option_in_module = 0
                        
                        self._xlog.info("Blue button pressed - moving to next option in module " + 
                                        self.application_modules[selected_module] + 
                                        ": " + options_in_current_module[selected_option_in_module])
                        time.sleep(0.2) # Debounce delay
                        should_refresh = True
                
                # Handle action in the current module by pressing the Green button
                if self.gpio.is_button_pressed("green"):
                    if self.application_modules[selected_module] in self.options_tree and selected_option_in_module != -1:
                        options_in_current_module = self.options_tree[self.application_modules[selected_module]]
                        option_key = options_in_current_module[selected_option_in_module]

                        self._xlog.info("Green button pressed - triggering action for option in module " + 
                                        self.application_modules[selected_module] + 
                                        ": " + option_key)
                        
                        # This is a bit hacky, but we want to show a "Please wait" modal message while performing the action.
                        modal_message = "Please wait..."
                        self.refresh_screen(
                            selected_module=selected_module,
                            selected_option_in_module=selected_option_in_module,
                            modal_message=modal_message,
                            modal_wait=modal_wait,
                            refresh_again=refresh_again
                        )

                        # Now trigger the action
                        modal_message = self.trigger_selected_option_action(
                            module_name=self.application_modules[selected_module],
                            option_key=option_key
                        )

                        # If we have a message to show, we set the flag to refresh the screen
                        if modal_message != "":
                            self._xlog.info(f"Action result: {modal_message}")
                            # Refresh the screen so the modal message is shown
                            should_refresh = True
                            # Wait for the modal message to be acknowledged
                            modal_wait = True

                    time.sleep(0.2) # Debounce delay

                # Run the selected module.
                # Must happen after the button press handling to avoid skipping modules.
                if should_refresh:

                    self.refresh_screen(
                        selected_module=selected_module,
                        selected_option_in_module=selected_option_in_module,
                        modal_message=modal_message,
                        modal_wait=modal_wait,
                        refresh_again=refresh_again
                    )

        except Exception as e:
            self._xlog.error(f"Exception in main run: {e}")
            self._xlog.debug(full_stack())
        except KeyboardInterrupt:
            self._xlog.info("Control + C detected")

        # However it happened, just close nicely.
        self.close_nicely()
    
    def refresh_screen(self, 
                       selected_module: int, 
                       selected_option_in_module: int, 
                       modal_message: str, 
                       modal_wait: bool,
                       refresh_again: bool = False):
        """
        Refresh the screen based on the selected module and option.
        """
        # Prepare the statusbar info common to all modules
        shared_data = Dictionary({
            # Data for the status bar
            "statusbar_show_time": self.STATUSBAR_SHOW_TIME,
            "statusbar_show_temperature": self.STATUSBAR_SHOW_TEMPERATURE,
            "statusbar_show_battery": self.STATUSBAR_SHOW_BATTERY,
            "battery_percentage": self.gathered_values.get("battery_percentage"),
            "battery_is_charging": self.gathered_values.get("battery_is_charging"),
            "temperature": self.gathered_values.get("temperature"),
            # Any message that we want to show in a modal window
            "modal_message": modal_message,
        })

        # We access the options in the current module if any was actually selected
        if self.application_modules[selected_module] in self.options_tree and selected_option_in_module != -1:
            options_in_current_module = self.options_tree[self.application_modules[selected_module]]

        # Temperature module
        if self.application_modules[selected_module] == ModuleDefinitions.TEMPERATURE:
            # Show temperature
            self._xlog.debug("Running Temperature module")
            self.display_temperature.module(parameters=shared_data.merge(Dictionary({
                "statusbar_show_temperature": False,  # Temperature module already shows temperature
                "temperature": self.gathered_values.get("temperature"),
                "humidity": self.gathered_values.get("humidity"),
                "air_pressure": self.gathered_values.get("air_pressure")
            })))
        
        # Accelerometer module
        elif self.application_modules[selected_module] == ModuleDefinitions.ACCELEROMETER:
            self._xlog.debug("Running Accelerometer module")
            self.display_accelerometer.module(parameters=shared_data.merge(Dictionary({
                "acceleration": self.gathered_values.get("acceleration"),
                "gyroscope": self.gathered_values.get("gyroscope"),
                "magnetometer": self.gathered_values.get("magnetometer"),
                "pitch_roll_yaw": self.gathered_values.get("pitch_roll_yaw"),
            })))
        
        # GPS module
        elif self.application_modules[selected_module] == ModuleDefinitions.GPS:
            self._xlog.debug("Running GPS module")
            self.display_gps.module(parameters=shared_data.merge(Dictionary({
                "gps_info": self.gathered_values.get("gps")
            })))

        # Power module
        elif self.application_modules[selected_module] == ModuleDefinitions.POWER:
            self._xlog.debug("Running Power module")
            self.display_power.module(parameters=shared_data.merge(Dictionary({
                "selected_option": options_in_current_module[selected_option_in_module] if selected_option_in_module != -1 else ""
            })))
        
        # Info module
        elif self.application_modules[selected_module] == ModuleDefinitions.INFO:
            self._xlog.debug("Running Info module")
            self.display_info.module(parameters=shared_data.merge(Dictionary({
                "os_info": System.get_os_info(),
                "network_interface": System.get_default_network_interface(),
                "wifi_network": System.get_connected_wifi_info()
            })))

        # Settings module
        elif self.application_modules[selected_module] == ModuleDefinitions.SETTINGS:
            self._xlog.debug("Running Settings module")
            self.display.module_settings(parameters=shared_data)
        
        # Unknown module
        else:
            self._xlog.debug("Selected module " + self.application_modules[selected_module] + " not implemented yet.")
            self.display.blank_screen(parameters=shared_data)
        
        # Did we show a modal message?
        if modal_message != "":
            # Wait 3 seconds to let the user read it
            if modal_wait:
                time.sleep(3)
            # Clear modal message after showing it
            modal_message = ""
            modal_wait = False
            # And refresh the screen again to remove it
            self._xlog.debug("Clearing modal message after showing it.")
            refresh_again = True

    def do_real_time_tasks(self, selected_module: int) -> bool:
        """
        Tasks that need to be done in real-time.
        Returns True if refreshing the screen is needed, False otherwise.

        Will not do too much logging here, as it pollutes the logs a lot.
        """
        
        # We avoid doing a lot of stuff here, as it is called for every loop iteration.
        # So, we only work on the given sensors if we're in the corresponding module.
        if self.application_modules[selected_module] == ModuleDefinitions.ACCELEROMETER:

            # Get accelerometer values
            accel_x, accel_y, accel_z = self.accelerometer.get_accelerometer_values()
            gyro_x, gyro_y, gyro_z = self.accelerometer.get_gyroscope_values()
            mag_x, mag_y, mag_z = self.accelerometer.get_magnetometer_values()
            # temp = self.accelerometer.get_temperature()
            pitch, roll, yaw = self.accelerometer.get_pitch_roll_yaw()

            self.gathered_values.set("acceleration", (accel_x, accel_y, accel_z))
            self.gathered_values.set("gyroscope", (gyro_x, gyro_y, gyro_z))
            self.gathered_values.set("magnetometer", (mag_x, mag_y, mag_z))
            self.gathered_values.set("pitch_roll_yaw", (pitch, roll, yaw))

            return True
        
        # if self.application_modules[selected_module] == ModuleDefinitions.GPS:
        #         # Get GPS position
        #         gps_info = self.gps.get_position()

        #         if gps_info is None:
        #             return False
                
        #         self.gathered_values.set("gps", {
        #             "latitude": gps_info.get("latitude", 0.0),
        #             "longitude": gps_info.get("longitude", 0.0),
        #             "direction_latitude": gps_info.get("direction_latitude", None),
        #             "direction_longitude": gps_info.get("direction_longitude", None),
        #             "altitude": gps_info.get("altitude", None),
        #             "altitude_units": gps_info.get("altitude_units", None),
        #             "timestamp": gps_info.get("timestamp", None),
        #             "status": gps_info.get("status", None),
        #         })
        #         return True

        return False
    
    def do_every_seconds_tasks(self, selected_module: int, seconds: int = None) -> bool:
        """
        Tasks that need to be done every given seconds.
        Returns True if refreshing the screen is needed, False otherwise.

        Will not do too much logging here, as it pollutes the logs a lot.
        """
        if seconds is None:
            seconds = self.SECONDS_TO_REACT_FOR_TASKS

        current_second = time.localtime().tm_sec
        triggering_second = self._last_processed_second + seconds
        if current_second >= triggering_second or (current_second == 0 and triggering_second >= 60):
            self._last_processed_second = current_second
            self._xlog.debug("🕐 New second detected: " + str(current_second) + f". Running every-second {self.SECONDS_TO_REACT_FOR_TASKS}s tasks.")

            if self.application_modules[selected_module] == ModuleDefinitions.GPS:
                # Get GPS position
                gps_info = self.gps.get_position()

                if gps_info is None:
                    return False
                
                self.gathered_values.set("gps", {
                    "latitude": gps_info.get("latitude", 0.0),
                    "longitude": gps_info.get("longitude", 0.0),
                    "direction_latitude": gps_info.get("direction_latitude", None),
                    "direction_longitude": gps_info.get("direction_longitude", None),
                    "altitude": gps_info.get("altitude", None),
                    "altitude_units": gps_info.get("altitude_units", None),
                    "timestamp": gps_info.get("timestamp", None),
                    "status": gps_info.get("status", None),
                })
                return True

        return False

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
                if current_temperature != self.gathered_values.get("temperature", 0):
                    self.gathered_values.set("temperature", current_temperature)
                    return_value = True

                current_humidity = round(self.temperature.get_humidity(), 1)
                if current_humidity != self.gathered_values.get("humidity", 0):
                    self.gathered_values.set("humidity", current_humidity)
                    return_value = True

                current_air_pressure = round(self.air_pressure.get_air_pressure(), 1)
                if current_air_pressure != self.gathered_values.get("air_pressure", 0):
                    self.gathered_values.set("air_pressure", current_air_pressure)
                    return_value = True

                if return_value:
                    self._xlog.info(f"Updated gathered values: Temperature={self.gathered_values.get('temperature')}°C, Humidity={self.gathered_values.get('humidity')}%, Air Pressure={self.gathered_values.get('air_pressure')} hPa")

            if self.STATUSBAR_SHOW_TIME:
                self._xlog.debug("Time change requires screen refresh.")
                return_value = True
            
            if self.STATUSBAR_SHOW_BATTERY:
                current_battery_percentage = math.ceil(self.ups.get_battery_percentage())
                if current_battery_percentage != self.gathered_values.get("battery_percentage", 0):
                    self.gathered_values.set("battery_percentage", current_battery_percentage)
                    return_value = True

                current_battery_is_charging = self.ups.is_charging()
                if current_battery_is_charging != self.gathered_values.get("battery_is_charging", False):
                    self.gathered_values.set("battery_is_charging", current_battery_is_charging)
                    return_value = True

            # We have a status change
            return return_value
        
        # No change in minute, no tasks to do
        return False
    
    def trigger_selected_option_action(self, module_name: str, option_key: str) -> str:
        self._xlog.info(f"Triggering action for {module_name}, option: {option_key}")
        returning_value = ""

        if module_name == ModuleDefinitions.POWER:

            if option_key == PowerActions.POWER_SHUTDOWN:
                if self._xconfig.get("ups.mock", False):
                    self._xlog.info("UPS is in mock mode, not shutting down.")
                else:
                    self._xlog.info("Shutting down")
                    self.close_nicely()
                    System.power_off_system()

            elif option_key == PowerActions.POWER_REBOOT:
                if self._xconfig.get("ups.mock", False):
                    self._xlog.info("UPS is in mock mode, not rebooting.")
                else:
                    self._xlog.info("Rebooting")
                    self.close_nicely()
                    System.reboot_system()

            elif option_key == PowerActions.POWER_UPDATE_RESTART:
                self._xlog.info("Updating and restarting application")
                system = System(config=self._xconfig, params=self._xparams)
                result = system.update_system()
                if result:
                    self._xlog.info("Update successful, restarting application")
                    self.close_nicely()
                    System.restart_program()
                else:
                    self._xlog.error("Update failed, not restarting application")
                    returning_value = "Update failed"
                    
        return returning_value


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
        
        # Close the GPIO
        if self.gpio is not None:
            self._xlog.debug("Closing GPIO")
            self.gpio.close()

        # Close the UPS
        if self.ups is not None:
            self._xlog.debug("Closing UPS")
            self.ups.close()
