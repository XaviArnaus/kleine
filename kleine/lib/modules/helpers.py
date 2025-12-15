from pyxavi import Dictionary, dd

from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

from PIL import ImageDraw, ImageFont
from datetime import datetime
import logging

class ScreenSections:

    STATUS_BAR_PICES_SPACING = 5 

    @staticmethod
    def shared_status_header(draw: ImageDraw.ImageDraw, parameters: dict):
        """
        Draw a shared status header for all modules
        """

        # Take in account that aligning right makes the text box to start from max_with downwards.
        # This means that we define the start drawing position from the corner up-right.

        # Define where to begin from the right.
        next_right_slot_x = parameters.get("screen_size").x - 5

        # Draw current time
        if parameters.get("statusbar_show_time", True):
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            draw.text(Point(next_right_slot_x, 5).to_image_point(),
                       text=time_str,
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_box_time = draw.textbbox(
                Point(next_right_slot_x, 5).to_image_point(),
                text=f"{parameters.get('battery_percentage', 0)}%",
                font=parameters.get("statusbar_font"),
                anchor="rt",
                align="right"
            )
            next_right_slot_x -= (bounding_box_time[2] - bounding_box_time[0]) + ScreenSections.STATUS_BAR_PICES_SPACING

        if parameters.get("statusbar_show_battery", True):

            # Next in the list is the battery percentage
            draw.text(Point(next_right_slot_x, 5).to_image_point(),
                       text=f"{parameters.get('battery_percentage', 0)}%",
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_box_battery = draw.textbbox(
                Point(next_right_slot_x, 5).to_image_point(),
                text=f"{parameters.get('battery_percentage', 0)}%",
                font=parameters.get("statusbar_font"),
                anchor="rt",
                align="right"
            )
            # Between the battery percentage and the icon, we do no spacing
            next_right_slot_x -= (bounding_box_battery[2] - bounding_box_battery[0])

            # Draw battery icon. We'll use 3 emojis: full battery, low battery, charging
            battery_icon = "🔋" if int(parameters.get('battery_percentage', 0)) > 30 else "🪫"
            battery_icon = "⚡" if parameters.get('battery_is_charging', False) else battery_icon
 
            draw.text(Point(next_right_slot_x, 4).to_image_point(),
                       text=battery_icon,
                       font=parameters.get("statusbar_font_emoji"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_emoji_battery = draw.textbbox(
                Point(next_right_slot_x, 4).to_image_point(),
                text=battery_icon,
                font=parameters.get("statusbar_font_emoji"),
                anchor="rt",
                align="right"
            )
            next_right_slot_x -= (bounding_emoji_battery[2] - bounding_emoji_battery[0]) + ScreenSections.STATUS_BAR_PICES_SPACING

        if parameters.get("statusbar_show_temperature", True):
            temperature = parameters.get("temperature", 0)
            draw.text(Point(next_right_slot_x, 5).to_image_point(),
                       text=f"{temperature}°C",
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
        
        # The left side is reserved for navigation icons: we show current module displayed.
        draw.text(Point(5, 5).to_image_point(),
                    text=f"{parameters.get('statusbar_nav_icon', '')}",
                    font=parameters.get("statusbar_font"),
                    fill=parameters.get("statusbar_font_color"),
                    anchor="lt",
                    align="left")
        
        # Draw a line between the title and the subtitle
        draw.line(Rectangle(Point(5, 26), Point(parameters.get("screen_size").x - 5, 26)).to_image_rectangle(),
                  fill=parameters.get("statusbar_font_color"),
                  width=1)

class Helpers:
    """
    Common module to provide shared functionality across different modules.
    """

    @staticmethod
    def wrap_text_if_needed(draw: ImageDraw.ImageDraw, text: str, max_width, font: ImageFont, logger: logging.Logger = None) -> str:
        try:
            width_text = draw.textlength(text.replace("\n", ""), font)
            if(width_text <= max_width):
                return text
            else:
                # Remove all possible current line breaks and then split by words
                words = text.replace("\n", " ").split(" ")
                new_text = ""
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line != "" else "") + word
                    width_test_line = draw.textlength(test_line, font)
                    if(width_test_line <= max_width):
                        current_line = test_line
                    else:
                        new_text += current_line + "\n"
                        current_line = word
                new_text += current_line
                return new_text
        except ValueError as e:
                if logger is None:
                    logger = logging.getLogger("Helpers")

                logger.error(f"Error wrapping text: {e}")
                logger.debug(text)

                return text
    
