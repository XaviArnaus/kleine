from PIL import ImageDraw,ImageFont

from pyxavi import Config, Dictionary

from kleine.lib.abstract.pyxavi import PyXavi
from .eink import Eink
from ..objects import Rectangle, Line, Point

class Macros(PyXavi):

    _display_size: Point = None

    def __init__(self, config: Config, params: Dictionary):
        super(Macros, self).init_pyxavi(config=config, params=params)

        self._display_size = Point(self._xconfig.get("display.size.x"), self._xconfig.get("display.size.y"))
    
    def load_or_create_statics(self,):
        '''
        Loads or creates the static images used in the macros.
        Currently, only the eyes images.

        It is meant to be called once at the initialization of the Display process,
        to have access to the singleton working image.
        '''
        pass
    
    def get_display_size(self) -> Point:
        return self._display_size

    def wrap_text_if_needed(self, canvas: ImageDraw.ImageDraw, text: str, max_width, font: ImageFont) -> str:
        try:
            width_text = canvas.textlength(text.replace("\n", ""), font)
            if(width_text <= max_width):
                return text
            else:
                # Remove all possible current line breaks and then split by words
                words = text.replace("\n", " ").split(" ")
                new_text = ""
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line != "" else "") + word
                    width_test_line = canvas.textlength(test_line, font)
                    if(width_test_line <= max_width):
                        current_line = test_line
                    else:
                        new_text += current_line + "\n"
                        current_line = word
                new_text += current_line
                return new_text
        except ValueError as e:
                self._xlog.error(f"Error wrapping text: {e}")
                return text

    def startup_splash(self, display: Eink):

        # First create a canvas
        canvas = display.create_canvas(reset_base_image=True)

        # Main title
        title = self._xconfig.get("app.name")
        version = self._xparams.get("app_version")
        canvas.text(Point(self._display_size.x / 2, self._display_size.y / 4).to_image_point(),
                    text = title + "  v" + version, 
                    font = display.FONT_BIG, 
                    fill = display.COLOR_BLACK,
                    anchor = "mm",
                    align = "center")
        
        # Draw a line between the title and the subtitle
        canvas.line(Rectangle(Point(5, self._display_size.y / 2), Point(self._display_size.x - 5, self._display_size.y / 2)).to_image_rectangle(),
                    fill = display.COLOR_BLACK,
                    width = 1)
        
        # # Subtitle
        # subtitle = "Chatbot: " + ("mocked" if self._xconfig.get("chatbot.mock", True) else "real") + \
        #             " | Display: " + ("mocked" if self._xconfig.get("display.mock", True) else "real") + \
        #             "\nSTT: " + ("mocked" if self._xconfig.get("speech-to-text.mock", True) else "real") + \
        #             " | TTS: " + ("mocked" if self._xconfig.get("text-to-speech.mock", True) else "real")
        # canvas.text(Point(self._display_size.x / 2, (self._display_size.y / 4) * 3).to_image_point(),
        #             text = subtitle, 
        #             font = display.FONT_MEDIUM, 
        #             fill = display.COLOR_BLACK,
        #             anchor = "mm",
        #             align = "center")
        
        # Now display the canvas
        display.display()

    def arbitrary_text_centered(self, display: Eink, text: str):

        canvas = display.create_canvas(reset_base_image=True)
        canvas.text(Point(self._display_size.x / 2, self._display_size.y / 2).to_image_point(),
                    text = text,
                    font = display.FONT_HUGE,
                    fill = display.COLOR_BLACK,
                    anchor = "mm",
                    align = "center")
        display.display(partial=True)

    def arbitrary_text_with_icon(
            self,
            display: Eink,
            text: str = None,
            icon: str = None,
            font_size: int = 24,
            header: str = None,
            font_header_size: int = 32,
            padding = 5) -> str:

        canvas = display.create_canvas(reset_base_image=True)

        # calculate anchor points and emojis for header and text
        if header and text:
            header_anchor = Point(self._display_size.x / 2, self._display_size.y / 3)
            text_anchor = Point(self._display_size.x / 2, (self._display_size.y / 4) * 3)
            header_emoji = icon + " " if icon else ""
            text_emoji = ""
        elif header and not text:
            header_anchor = Point(self._display_size.x / 2, self._display_size.y / 2)
            header_emoji = icon + " " if icon else ""
        elif not header and text:
            text_anchor = Point(self._display_size.x / 2, self._display_size.y / 2)
            text_emoji = icon + " " if icon else ""

        if header:
            canvas.text(header_anchor.to_image_point(),
                text = f"{header_emoji}{header}",
                font = display.get_font_by_size(font_header_size),
                fill = display.COLOR_BLACK,
                anchor = "mm",
                align = "center")

        if text:
            font = display.get_font_by_size(font_size)
            padding = 5
            value = self.wrap_text_if_needed(
                canvas=canvas,
                text=f"{text_emoji}{text}",
                max_width=self._display_size.x - (2 * padding),
                font=font
            )
            canvas.multiline_text(text_anchor.to_image_point(),
                text = value,
                font = font,
                fill = display.COLOR_BLACK,
                anchor = "mm",
                align = "center")
        
        display.display()

    def soft_clear(self, display: Eink):

        # First create a canvas
        canvas = display.create_canvas(reset_base_image=True)

        # Create a white rectancgle with the sizes of the screen
        rect_1 = Point(0, 0)
        rect_2 = Point(self._display_size.x, self._display_size.y)
        canvas.rectangle(
            Rectangle(rect_1, rect_2).to_image_rectangle(),
            outline=display.COLOR_WHITE,
            fill=display.COLOR_WHITE)

        # Now display the canvas
        display.display()