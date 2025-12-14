from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from PIL import ImageDraw, ImageFont
import logging

class Helpers(PyXavi):
    """
    Common module to provide shared functionality across different modules.
    """

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Helpers, self).init_pyxavi(config=config, params=params)

    @staticmethod
    def wrap_text_if_needed(canvas: ImageDraw.ImageDraw, text: str, max_width, font: ImageFont, logger: logging.Logger = None) -> str:
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
                if logger is None:
                    logger = logging.getLogger("Helpers")

                logger.error(f"Error wrapping text: {e}")
                logger.debug(text)

                return text