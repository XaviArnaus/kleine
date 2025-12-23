from pyxavi import Dictionary, dd

from kleine.lib.objects.module_definitions import ModuleDefinitions
from kleine.lib.objects.gps_signal_quality import GPSSignalQuality
from kleine.lib.objects.wifi_signal_quality import WifiSignalQuality

from kleine.lib.objects.point import Point
from kleine.lib.objects.rectangle import Rectangle

from PIL import ImageDraw, ImageFont
from datetime import datetime
import logging

class ScreenSections:

    STATUS_BAR_PICES_SPACING = 5 

    @staticmethod
    def shared_status_header(draw: ImageDraw.ImageDraw, parameters: Dictionary):
        """
        Draw a shared status header for all modules
        """

        # Take in account that aligning right makes the text box to start from max_with downwards.
        # This means that we define the start drawing position from the corner up-right.

        screen_size: Point = parameters.get("screen_size")

        # Define where to begin from the right.
        next_right_slot_x = screen_size.x - 5

        # Draw current time
        if parameters.get("statusbar_show_time", True):
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            draw.text((next_right_slot_x, 5),
                       text=time_str,
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_box_time = draw.textbbox(
                (next_right_slot_x, 5),
                text=f"{parameters.get('battery_percentage', 0)}%",
                font=parameters.get("statusbar_font"),
                anchor="rt",
                align="right"
            )
            # For any reason we need extra spacing after the time
            next_right_slot_x -= (bounding_box_time[2] - bounding_box_time[0]) + 12 + ScreenSections.STATUS_BAR_PICES_SPACING

        if parameters.get("statusbar_show_battery", True):

            # Next in the list is the battery percentage
            draw.text((next_right_slot_x, 5),
                       text=f"{parameters.get('battery_percentage', 0)}%",
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_box_battery = draw.textbbox(
                (next_right_slot_x, 5),
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
            battery_icon_color = parameters.get("color.green") if int(parameters.get('battery_percentage', 0)) > 60 else \
                parameters.get("color.orange") if int(parameters.get('battery_percentage', 0)) > 30 else parameters.get("color.red")
            battery_icon_color = parameters.get("color.green") if parameters.get('battery_is_charging', False) else battery_icon_color

            draw.text((next_right_slot_x, 4),
                       text=battery_icon,
                       font=parameters.get("statusbar_font_emoji"),
                       fill=battery_icon_color,
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_emoji_battery = draw.textbbox(
                (next_right_slot_x, 4),
                text=battery_icon,
                font=parameters.get("statusbar_font_emoji"),
                anchor="rt",
                align="right"
            )
            next_right_slot_x -= (bounding_emoji_battery[2] - bounding_emoji_battery[0]) + ScreenSections.STATUS_BAR_PICES_SPACING

        if parameters.get("statusbar_show_temperature", True):
            temperature = parameters.get("temperature", 0)
            draw.text((next_right_slot_x, 5),
                       text=f"{temperature}°C",
                       font=parameters.get("statusbar_font"),
                       fill=parameters.get("statusbar_font_color"),
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_emoji_temperature = draw.textbbox(
                (next_right_slot_x, 4),
                text=f"{temperature}°C",
                font=parameters.get("statusbar_font_emoji"),
                anchor="rt",
                align="right"
            )
            next_right_slot_x -= (bounding_emoji_temperature[2] - bounding_emoji_temperature[0]) + (ScreenSections.STATUS_BAR_PICES_SPACING  * 3)

        if parameters.get("statusbar_show_gps_signal_quality", True):

            signal_quality = parameters.get("gps_signal_quality", GPSSignalQuality.SIGNAL_UNKNOWN)

            match signal_quality:
                case GPSSignalQuality.SIGNAL_GOOD:
                    gps_icon_color = parameters.get("color.green")
                case GPSSignalQuality.SIGNAL_WEAK:
                    gps_icon_color = parameters.get("color.orange")
                case GPSSignalQuality.SIGNAL_POOR:
                    gps_icon_color = parameters.get("color.red")
                case GPSSignalQuality.SIGNAL_UNKNOWN:
                    gps_icon_color = parameters.get("color.white")

            draw.text((next_right_slot_x, 4),
                       text=f"📶",
                       font=parameters.get("statusbar_font_emoji"),
                       fill=gps_icon_color,
                       anchor="rt",
                       align="right")
            # Update next right slot position
            bounding_emoji_signal = draw.textbbox(
                (next_right_slot_x, 4),
                text=f"📶",
                font=parameters.get("statusbar_font_emoji"),
                anchor="rt",
                align="right"
            )
            next_right_slot_x -= (bounding_emoji_signal[2] - bounding_emoji_signal[0]) + ScreenSections.STATUS_BAR_PICES_SPACING

        if parameters.get("statusbar_show_wifi_signal_quality", True):

            signal_quality = parameters.get("wifi_signal_quality", WifiSignalQuality.SIGNAL_UNKNOWN)

            match signal_quality:
                case WifiSignalQuality.SIGNAL_GOOD:
                    wifi_icon_color = parameters.get("color.green")
                case WifiSignalQuality.SIGNAL_WEAK:
                    wifi_icon_color = parameters.get("color.orange")
                case WifiSignalQuality.SIGNAL_POOR:
                    wifi_icon_color = parameters.get("color.red")
                case WifiSignalQuality.SIGNAL_UNKNOWN:
                    wifi_icon_color = parameters.get("color.white")

            draw.text((next_right_slot_x, 4),
                       text=f"🛜",
                       font=parameters.get("statusbar_font_emoji"),
                       fill=wifi_icon_color,
                       anchor="rt",
                       align="right")
            # # Update next right slot position
            # bounding_emoji_signal = draw.textbbox(
            #     (next_right_slot_x, 4),
            #     text=f"🛜",
            #     font=parameters.get("statusbar_font_emoji"),
            #     anchor="rt",
            #     align="right"
            # )
            # next_right_slot_x -= (bounding_emoji_signal[2] - bounding_emoji_signal[0]) + ScreenSections.STATUS_BAR_PICES_SPACING

        # The left side is reserved for navigation icons: we show current module displayed.
        draw.text((5, 5),
                    text=f"{parameters.get('statusbar_nav_icon', '')}",
                    font=parameters.get("statusbar_font_emoji"),
                    fill=parameters.get("statusbar_font_color"),
                    anchor="lt",
                    align="left")
        
        # Draw a line between the title and the subtitle
        draw.line(Rectangle(Point(5, 26), Point(screen_size.x - 5, 26)).to_image_rectangle(),
                  fill=parameters.get("statusbar_font_color"),
                  width=1)
    
    @staticmethod
    def shared_status_footer(draw: ImageDraw.ImageDraw, parameters: Dictionary):
        """
        Draw a shared status footer for all modules
        """

        screen_size: Point = parameters.get("screen_size")
        line_y = screen_size.y - 26
        icon_y = screen_size.y - 4
        text_y = screen_size.y - 1

        # What is the module we're in?
        module_name = parameters.get("current_module", None)

        # We first present the crossing line
        draw.line(Rectangle(Point(5, line_y), Point(screen_size.x - 5, line_y)).to_image_rectangle(),
                  fill=parameters.get("statusbar_font_color"),
                  width=1)
        
        # We always show the yellow button on the left
        bounding_yellow_dot = draw.textbbox(
            (5, icon_y),
            text="🟡",
            font=parameters.get("statusbar_font_emoji"),
            anchor="lb",
            align="left")
        draw.text((5, icon_y),
            text="🟡",
            font=parameters.get("statusbar_font_emoji"),
            fill=parameters.get("color.yellow"),
            anchor="lb",
            align="left")
        yellow_text_x = 5 + (bounding_yellow_dot[2] - bounding_yellow_dot[0]) + ScreenSections.STATUS_BAR_PICES_SPACING
        draw.text((yellow_text_x, text_y),
            text="App",
            font=parameters.get("statusbar_font"),
            fill=parameters.get("statusbar_font_color"),
            anchor="lb",
            align="left")
        
        if module_name is not None and module_name == ModuleDefinitions.POWER:
            # Show the blue button on the center
            bounding_blue_button = draw.textbbox(
                (screen_size.x / 2, icon_y),
                text="🔵",
                font=parameters.get("statusbar_font_emoji"),
                anchor="mb",
                align="center")
            bounding_blue_text = draw.textbbox(
                (screen_size.x / 2, text_y - 4),
                text="Select",
                font=parameters.get("statusbar_font"),
                anchor="mb",
                align="center")
            blue_button_x = screen_size.x / 2 - \
                            ( \
                                (bounding_blue_button[2] - bounding_blue_button[0]) + \
                                ScreenSections.STATUS_BAR_PICES_SPACING + \
                                (bounding_blue_text[2] - bounding_blue_text[0]) \
                            ) / 2
            blue_text_x = blue_button_x + \
                            ( \
                                (bounding_blue_button[2] - bounding_blue_button[0]) + \
                                ScreenSections.STATUS_BAR_PICES_SPACING * 2 + \
                                (bounding_blue_text[2] - bounding_blue_text[0]) \
                            ) / 2
            draw.text((blue_button_x, icon_y),
                text="🔵",
                font=parameters.get("statusbar_font_emoji"),
                fill=parameters.get("color.blue"),
                anchor="mb",
                align="center")
            draw.text((blue_text_x, text_y - 4),
                text="Select",
                font=parameters.get("statusbar_font"),
                fill=parameters.get("statusbar_font_color"),
                anchor="mb",
                align="center")
            
            # Show the green button on the right
            bounding_green_text = draw.textbbox(
                (screen_size.x - 5, text_y - 4),
                text="Enter",
                font=parameters.get("statusbar_font"),
                anchor="rb",
                align="right")
            draw.text((screen_size.x - 5, text_y - 4),
                text="Enter",
                font=parameters.get("statusbar_font"),
                fill=parameters.get("statusbar_font_color"),
                anchor="rb",
                align="right")
            green_button_x = screen_size.x - 5 - (bounding_green_text[2] - bounding_green_text[0]) - ScreenSections.STATUS_BAR_PICES_SPACING
            draw.text((green_button_x, icon_y),
                text="🟢",
                font=parameters.get("statusbar_font_emoji"),
                fill=parameters.get("color.green"),
                anchor="rb",
                align="right")

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
    
