from pyxavi import Dictionary
from kleine.lib.abstract.display_module import DisplayModule
from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

class DisplayAccelerometer(DisplayModule):

    

    def module(self, parameters: Dictionary = None):
        """
        Show the power module on the display
        """
        self._xlog.info("Showing power module, selected option: " + parameters.get("selected_option", "none"))
        draw = self.canvas.get_canvas()

        # Draw a rectangle over the entire screen
        draw.rectangle(Rectangle(Point(0, 0), self.screen_size).to_image_rectangle(),
                       fill=self.canvas.COLOR_BLACK)
        
        # Prepare the data:
        acc_x, acc_y, acc_z = parameters.get("acceleration", (0, 0, 0))
        gyro_x, gyro_y, gyro_z = parameters.get("gyroscope", (0, 0, 0))
        mag_x, mag_y, mag_z = parameters.get("magnetometer", (0, 0, 0))
        pitch, roll, yaw = parameters.get("pitch_roll_yaw", (0.0, 0.0, 0.0))
        
        # Prepare the string to show
        info_text = [
            f"Accel:  x:{acc_x} | y:{acc_y} | z:{acc_z}",
            f"Gyro:   x:{gyro_x} | y:{gyro_y} | z:{gyro_z}",
            f"Magnet: x:{mag_x} | y:{mag_y} | z:{mag_z}",
            f"\nPitch: {round(pitch, 1)} | Roll: {round(roll, 1)} | Yaw: {round(yaw, 1)}",
        ]
        info_text_str = "\n".join(info_text)

        draw.text(Point(10, 50).to_image_point(),
                   text=info_text_str,
                   font=self.canvas.FONT_TINY,
                   fill=self.canvas.COLOR_WHITE,
                   align="left")

        # All modules should share a similar status header
        if parameters.get("statusbar_active", True):
            self._shared_status_header(draw, parameters, "🛩️")

        # Show modal message if any
        self._shared_modal_message(draw, parameters)

        self._flush_canvas_to_device()
