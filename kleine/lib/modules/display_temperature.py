from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point

class DisplayTemperature(DisplayModule):

    def module(self, parameters: Dictionary = None):
        """
        Show the current temperature on the display
        """
        self._xlog.debug("Showing current temperature...")
        draw = self.canvas.get_canvas()

        # All modules should share a similar status header
        self._shared_status_header(draw, parameters, "🌡")
        self._shared_status_footer(draw, parameters)

        # Print the temperature in the middle of the screen
        draw.text(Point((self.screen_size.x / 2) - 5, self.screen_size.y / 2).to_image_point(),
                   text=f"{parameters.get('temperature', 0)}°C",
                   font=self.canvas.FONT_ULTRA,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        draw.text(Point((self.screen_size.x / 2) - 5, (self.screen_size.y / 4) * 3).to_image_point(),
                   text=f"💧 {parameters.get('humidity', 0)}%  🌦️ {parameters.get('air_pressure', 0)} hPa",
                   font=self.canvas.FONT_MEDIUM,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        self._flush_canvas_to_device()
