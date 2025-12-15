from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayInfo(DisplayModule):

    def module(self, parameters: Dictionary = None):
        """
        Show the information module on the display
        """
        self._xlog.info("Showing information module...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        # Prepare the info text
        os_data: dict = parameters.get("os_info", {})
        network_interface: dict = parameters.get("network_interface", {})
        wifi_network: list[dict] = parameters.get("wifi_network", [])
        info_text = [
            f"OS & arch: {os_data.get('system', 'N/A')} / {os_data.get('machine', 'N/A')}",
            f"IP address: {network_interface.get('ip', 'N/A')}",
            f"MAC address: {network_interface.get('mac', 'N/A')}",
            f"Wifi SSID: {wifi_network[0].get('ssid', 'N/A')}" if wifi_network else "Wifi SSID: N/A",
            f"Wifi Sec: {wifi_network[0].get('security', 'N/A')}" if wifi_network else "Wifi Sec: N/A",
            f"Wifi Signal: {wifi_network[0].get('signal', 'N/A')}" if wifi_network else "Wifi Signal: N/A",
        ]
        info_text_str = "\n".join(info_text)

        draw.text(Point(10, 50).to_image_point(),
                   text=info_text_str,
                   font=self.canvas.FONT_MEDIUM,
                   fill=self.canvas.COLOR_WHITE,
                   align="left")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "ℹ️")

        self._flush_canvas_to_device()
