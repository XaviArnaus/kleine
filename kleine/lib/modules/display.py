from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle
from kleine.lib.modules.helpers import Helpers

class Display(DisplayModule):
    """
    Display module abstract the graphical interaction to the user

    It uses a Canvas to draw things on the screen and then sends them to the display device.
    Because we could have several displays at the same time (e.g., LCD and eInk), this module
    expects to receive a Canvas instance where to draw and a device instance where to send the final image.
    """

    def startup_splash(self):
        """
        Show a startup splash screen
        """
        self._xlog.debug("Showing startup splash screen...")
        draw = self.canvas.get_canvas()
        
        # Main title
        title = self._xconfig.get("app.name")
        version = self._xparams.get("app_version")
        draw.text(Point(self.screen_size.x / 2, self.screen_size.y / 4).to_image_point(),
                   text=title + "  v" + version,
                   font=self.canvas.FONT_BIG,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")
        
        # Draw a line between the title and the subtitle
        draw.line(Rectangle(Point(5, self.screen_size.y / 2), Point(self.screen_size.x - 5, self.screen_size.y / 2)).to_image_rectangle(),
                  fill=self.canvas.COLOR_WHITE,
                  width=1)

        # Subtitle
        subtitle = "GPIO: " + ("mocked" if self._xconfig.get("gpio.mock", True) else "real") + \
                    " | LCD: " + ("mocked" if self._xconfig.get("lcd.mock", True) else "real") + \
                    " | Temperature: " + ("mocked" if self._xconfig.get("temperature.mock", True) else "real") + \
                    " | Humidity: " + ("mocked" if self._xconfig.get("humidity.mock", True) else "real") + \
                    " | Air Pressure: " + ("mocked" if self._xconfig.get("air_pressure.mock", True) else "real") + \
                    " | UPS: " + ("mocked" if self._xconfig.get("ups.mock", True) else "real")
        draw.text(Point(self.screen_size.x / 2, (self.screen_size.y / 4) * 3).to_image_point(),
                   text=Helpers.wrap_text_if_needed(
                       draw, 
                       subtitle, 
                       self.screen_size.x - 10, 
                       self.canvas.FONT_TINY, 
                       self._xlog),
                   font=self.canvas.FONT_TINY,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        self._flush_canvas_to_device()

    def module_accelerometer(self, parameters: Dictionary = None):
        """
        Show the accelerometer readings on the display
        """
        self._xlog.info("Showing accelerometer readings...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        draw.text(Point(self.screen_size.x / 2, self.screen_size.y / 2).to_image_point(),
                   text="🛩️",
                   font=self.canvas.FONT_ULTRA,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "🛩️")

        self._flush_canvas_to_device()
    
    def module_settings(self, parameters: Dictionary = None):
        """
        Show the settings module on the display
        """
        self._xlog.info("Showing settings module...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        draw.text(Point(self.screen_size.x / 2, self.screen_size.y / 2).to_image_point(),
                   text="⚙️",
                   font=self.canvas.FONT_ULTRA,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "⚙️")

        self._flush_canvas_to_device()
    
    def blank_screen(self, parameters: Dictionary = None):
        """
        Show a blank screen on the display.
        """
        self._xlog.info("Showing blank screen...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters)

        self._flush_canvas_to_device()