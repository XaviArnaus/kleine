from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.objects.errors import LackOfSetupError
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle
from kleine.lib.modules.helpers import Helpers

from PIL import ImageDraw
from datetime import datetime

class Display(PyXavi):
    """
    Display module abstract the graphical interaction to the user

    It uses a Canvas to draw things on the screen and then sends them to the display device.
    Because we could have several displays at the same time (e.g., LCD and eInk), this module
    expects to receive a Canvas instance where to draw and a device instance where to send the final image.
    """

    canvas: Canvas = None
    device: Lcd = None

    screen_size: Point = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Display, self).init_pyxavi(config=config, params=params)

        # We're supposed to receive a canvas where to draw
        if not params.key_exists("canvas"):
            self._xlog.error("No canvas provided to display module")
            raise LackOfSetupError("No canvas provided to display module")
        self.canvas = params.get("canvas")

        # We're supposed to receive a device where to send the final image
        if not params.key_exists("device"):
            self._xlog.error("No device provided to display module")
            raise LackOfSetupError("No device provided to display module")
        self.device = params.get("device")

        self.screen_size = self.canvas.get_screen_size()

    def startup_splash(self):
        """
        Show a startup splash screen
        """
        self._xlog.info("Showing startup splash screen...")
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
                    " | Sense: " + ("mocked" if self._xconfig.get("sense.mock", True) else "real") + \
                    " | UPS: " + ("mocked" if self._xconfig.get("ups.mock", True) else "real")
        draw.text(Point(self.screen_size.x / 2, (self.screen_size.y / 4) * 3).to_image_point(),
                   text=Helpers.wrap_text_if_needed(
                       draw, 
                       subtitle, 
                       self.screen_size.x - 10, 
                       self.canvas.FONT_MEDIUM, 
                       self._xlog),
                   font=self.canvas.FONT_MEDIUM,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        self._flush_canvas_to_device()
    
    def _shared_status_header(self, draw: ImageDraw.ImageDraw, parameters: Dictionary):
        """
        Draw a shared status header for all modules
        """

        if parameters.get("statusbar_show_time", True):
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            draw.text(Point(self.screen_size.x - 5, 5).to_image_point(),
                       text=time_str,
                       font=self.canvas.FONT_SMALL,
                       fill=self.canvas.COLOR_WHITE,
                       anchor="rt",
                       align="right")

        if parameters.get("statusbar_show_temperature", True):
            temperature = parameters.get("temperature", 0)
            draw.text(Point(5, 5).to_image_point(),
                       text=f"{temperature}°C",
                       font=self.canvas.FONT_SMALL,
                       fill=self.canvas.COLOR_WHITE,
                       anchor="lt",
                       align="left")
        
        # Draw a line between the title and the subtitle
        draw.line(Rectangle(Point(5, 15), Point(self.screen_size.x - 5, 15)).to_image_rectangle(),
                  fill=self.canvas.COLOR_WHITE,
                  width=1)

    def module_temperature(self, parameters: Dictionary = None):
        """
        Show the current temperature on the display
        """
        self._xlog.info("Showing current temperature...")
        draw = self.canvas.get_canvas()

        # All modules should share a similar status header
        self._shared_status_header(draw, parameters)

        # Print the value
        draw.text(Point(self.screen_size.x / 2, self.screen_size.y / 2).to_image_point(),
                   text=f"{parameters.get('temperature', 0)}°C",
                   font=self.canvas.FONT_ULTRA,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

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

    def _flush_canvas_to_device(self):
        """
        Send the current canvas image to the display device
        """
        self._xlog.debug("Flushing canvas to display device...")
        image = self.canvas.get_image()
        self.device.flush_to_device(image)