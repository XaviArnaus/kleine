from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayPower(DisplayModule):

    options = {
        "shutdown": "⛔️ Shut down",
        "reboot": "♻️ Reboot",
        "update_restart": "🆙 Update and restart"
    }

    def module(self, parameters: Dictionary = None, selected_option: str = ""):
        """
        Show the power module on the display
        """
        self._xlog.info("Showing power module...")
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        for key, description in self.options.items():
            option_text = description
            if key == selected_option:
                draw.rectangle(Rectangle(Point(10, 50 + (list(self.options.keys()).index(key) * 30)), Point(10 + self.screen_size.x - 20, 50 + (list(self.options.keys()).index(key) * 30) + 30)).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
                draw.text(Point(10, 50 + (list(self.options.keys()).index(key) * 30)).to_image_point(),
                       text=option_text,
                       font=self.canvas.FONT_MEDIUM,
                       fill=self.canvas.COLOR_BLACK,
                       align="left")
            else:   
                draw.text(Point(10, 50 + (list(self.options.keys()).index(key) * 30)).to_image_point(),
                        text=option_text,
                        font=self.canvas.FONT_MEDIUM,
                        fill=self.canvas.COLOR_WHITE,
                        align="left")
        

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "⛔️")

        self._flush_canvas_to_device()
