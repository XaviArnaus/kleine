from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.canvas.canvas import Canvas
from kleine.lib.lcd.lcd import Lcd
from kleine.lib.objects.errors import LackOfSetupError
from kleine.lib.objects.point import Point
from kleine.lib.modules.helpers import ScreenSections

from PIL import ImageDraw

class DisplayModule(PyXavi):
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
        super(DisplayModule, self).init_pyxavi(config=config, params=params)

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
    
    def _shared_status_header(self, draw: ImageDraw.ImageDraw, parameters: Dictionary, module_icon: str = ""):
        ScreenSections.shared_status_header(draw, {
            **parameters.to_dict(),
            "statusbar_nav_icon": module_icon,
            "statusbar_font": self.canvas.FONT_SMALL,
            "statusbar_font_emoji": self.canvas.FONT_SMALL_EMOJI,
            "statusbar_font_color": self.canvas.COLOR_WHITE,
            "screen_size": self.screen_size
        })

    def _flush_canvas_to_device(self):
        """
        Send the current canvas image to the display device
        """
        self._xlog.debug("Flushing canvas to display device...")
        image = self.canvas.get_image()
        self.device.flush_to_device(image)