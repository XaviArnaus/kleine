from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle
from kleine.lib.objects.module_definitions import PowerActions

class DisplayPower(DisplayModule):

    options = {
        PowerActions.POWER_SHUTDOWN: "⛔️ Shut down",
        PowerActions.POWER_REBOOT: "♻️ Reboot",
        PowerActions.POWER_UPDATE_RESTART: "🆙 Update and restart"
    }

    def module(self, parameters: Dictionary = None):
        """
        Show the power module on the display
        """
        self._xlog.debug("Showing power module, selected option: " + parameters.get("selected_option", "none"))
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        for key, description in self.options.items():
            option_text = description
            if key == parameters.get("selected_option"):
                draw.rectangle(Rectangle(Point(10, 50 + (list(self.options.keys()).index(key) * 30)), Point(10 + self.screen_size.x - 20, 50 + (list(self.options.keys()).index(key) * 30) + 30)).to_image_rectangle(),
                       fill=self.canvas.COLOR_WHITE)
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

        # Show modal message if any
        self._shared_modal_message(draw, parameters)
        self._shared_status_footer(draw, parameters)

        self._flush_canvas_to_device()
