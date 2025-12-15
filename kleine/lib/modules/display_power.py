from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayPower(DisplayModule):

    def module(self, parameters: Dictionary = None):
        """
        Show the power module on the display
        """
        self._xlog.info("Showing power module...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        draw.text(Point(self.screen_size.x / 2, self.screen_size.y / 2).to_image_point(),
                   text="⛔️",
                   font=self.canvas.FONT_ULTRA,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "⛔️")

        self._flush_canvas_to_device()
