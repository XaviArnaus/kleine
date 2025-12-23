from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayCockpit(DisplayModule):

    def module(self, parameters: Dictionary = None):
        """
        Show the Cockpit module on the display
        """
        self._xlog.debug("Showing Cockpit module")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)

        # Prepare the GPS text
        gps_data: dict = parameters.get("gps_info", {})
        
        draw.text(Point((self.screen_size.x / 2), (self.screen_size.y / 2) - 15).to_image_point(),
                   text=f"{gps_data.get('speed', 'N/A')} km/h",
                   font=self.canvas.FONT_HUGE,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")
        
        draw.text(Point((self.screen_size.x / 2), ((self.screen_size.y / 4) * 3) - 15).to_image_point(),
                   text=f"🏔️ {gps_data.get('altitude', 'N/A')} {gps_data.get('altitude_units', '')}",
                   font=self.canvas.FONT_MEDIUM,
                   fill=self.canvas.COLOR_WHITE,
                   anchor="mm",
                   align="center")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "🚗")
            self._shared_status_footer(draw, parameters)
        
        self._shared_modal_message(draw, parameters)

        self._flush_canvas_to_device()
