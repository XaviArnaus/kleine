from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayGPS(DisplayModule):

    def module(self, parameters: Dictionary = None):
        """
        Show the GPS module on the display
        """
        self._xlog.debug("Showing GPS module")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)

        # Prepare the GPS text
        gps_data: dict = parameters.get("gps_info", {})
        gps_text = [
            f"Latitude: {gps_data.get('latitude', 'N/A')} {gps_data.get('direction_latitude', '')}",
            f"Longitude: {gps_data.get('longitude', 'N/A')} {gps_data.get('direction_longitude', '')}",
            f"Altitude: {gps_data.get('altitude', 'N/A')} {gps_data.get('altitude_units', '')}",
            f"Speed: {gps_data.get('speed', 'N/A')} km/h",
            f"Status: {gps_data.get('status', 'N/A')}",
            # f"Timestamp: {gps_data.get('timestamp').isoformat() if gps_data.get('timestamp') else 'N/A'}",
            f"Signal Quality: {gps_data.get('signal_quality', 'N/A')}",
        ]
        gps_text_str = "\n".join(gps_text)

        draw.text(Point(10, 50).to_image_point(),
                   text=gps_text_str,
                   font=self.canvas.FONT_SMALL,
                   fill=self.canvas.COLOR_WHITE,
                   align="left")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "📡")
            self._shared_status_footer(draw, parameters)
        
        self._shared_modal_message(draw, parameters)

        self._flush_canvas_to_device()
