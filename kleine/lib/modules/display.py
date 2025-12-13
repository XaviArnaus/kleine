from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.objects.errors import LackOfSetupError
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

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
                   fill=self.canvas.COLOR_BLACK,
                   anchor="mm",
                   align="center")
        
        # Draw a line between the title and the subtitle
        draw.line(Rectangle(Point(5, self.screen_size.y / 2), Point(self.screen_size.x - 5, self.screen_size.y / 2)).to_image_rectangle(),
                  fill=self.canvas.COLOR_BLACK,
                  width=1)

        # # Subtitle
        # subtitle = "Chatbot: " + ("mocked" if self._xconfig.get("chatbot.mock", True) else "real") + \
        #             " | Display: " + ("mocked" if self._xconfig.get("display.mock", True) else "real") + \
        #             "\nSTT: " + ("mocked" if self._xconfig.get("speech-to-text.mock", True) else "real") + \
        #             " | TTS: " + ("mocked" if self._xconfig.get("text-to-speech.mock", True) else "real")
        # draw.text(Point(self.screen_size.x / 2, (self.screen_size.y / 4) * 3).to_image_point(),
        #            text=subtitle,
        #            font=self.canvas.FONT_MEDIUM,
        #            fill=self.canvas.COLOR_BLACK,
        #            anchor="mm",
        #            align="center")

        self._flush_canvas_to_device()


    def _flush_canvas_to_device(self):
        """
        Send the current canvas image to the display device
        """
        self._xlog.debug("Flushing canvas to display device...")
        image = self.canvas.get_image()
        self.device.display_image(image)