import os
import sys 
import time
import logging
import spidev as SPI
# sys.path.append("..")
from .ST7789 import ST7789
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from kleine.lib.objects.point import Point

from definitions import ROOT_DIR

class Lcd(PyXavi):

    DEVICE = {
        "SPI_BUS": 0,
        "SPI_DEVICE": 0,
        "RST_PIN": 27,
        "DC_PIN": 25,
        "BL_PIN": 12,
        "BRIGHTNESS": 255
    }

    FONT_PATH = os.path.join(ROOT_DIR, "kleine", "lib", "lcd", "fonts")
    PIC_PATH = os.path.join(ROOT_DIR, "kleine", "lib", "lcd", "pic")

    DEFAULT_STORAGE_PATH = "storage/"
    DEFAULT_MOCKED_IMAGES_PATH = "mocked/lcd/"

    driver: ST7789 = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Lcd, self).init_pyxavi(config=config, params=params)

        # Initialise the LCD display
        self._xlog.info("Initialising LCD display...")
        self._xlog.debug(f"SPI Bus={self.DEVICE['SPI_BUS']}, Device={self.DEVICE['SPI_DEVICE']}")
        self._xlog.debug(f"GPIO RST={self.DEVICE['RST_PIN']}, DC={self.DEVICE['DC_PIN']}, BL={self.DEVICE['BL_PIN']}")
        self.driver = self.get_driver()

    def get_driver(self) -> ST7789:
        """
        Get the LCD driver instance as a singleton
        """
        if self.driver is None:
            self.driver = ST7789(
                spi=SPI.SpiDev(
                    self._xconfig.get("lcd.hardware.bus", self.DEVICE["SPI_BUS"]),
                    self._xconfig.get("lcd.hardware.device", self.DEVICE["SPI_DEVICE"])
                ),
                rst=self._xconfig.get("lcd.hardware.RST", self.DEVICE["RST_PIN"]),
                dc=self._xconfig.get("lcd.hardware.DC", self.DEVICE["DC_PIN"]),
                bl=self._xconfig.get("lcd.hardware.BL", self.DEVICE["BL_PIN"])
            )
            # Initialize library.
            self.driver.Init()
            # Clear display.
            self.driver.clear()
            #Set the backlight to 100
            self.driver.bl_DutyCycle(self._xconfig.get("lcd.hardware.brightness", self.DEVICE["BRIGHTNESS"]))
        return self.driver

    def get_screen_size(self) -> Point:
        """
        Get the screen size as a tuple (width, height)
        """
        return Point(self.driver.width, self.driver.height)
    
    def display_image(self, image: Image.Image):
        """
        Displays an image on the LCD display.

        Args:
            image: The image to display.
        """
        if (not self._is_gpio_allowed()):
            file_path = self._xconfig.get("storage.path", self.DEFAULT_STORAGE_PATH) + self.DEFAULT_MOCKED_IMAGES_PATH + datetime.now().strftime("%Y%m%d-%H%M%S.%f") + ".png"
            image.save(file_path)
            file_path = self._xconfig.get("storage.path", self.DEFAULT_STORAGE_PATH) + self.DEFAULT_MOCKED_IMAGES_PATH + "_latest.png"
            image.save(file_path)
        else:
            self.flush_to_device(image)

    def flush_to_device(self, image: Image.Image):
        if self._xconfig.get("lcd.rotate", False):
                image = image.rotate(180)
        self.driver.ShowImage(image)
    
    def _is_gpio_allowed(self):
        import platform

        os = platform.system()        
        if (os.lower() != "linux"):
            self._xlog.warning("OS is not Linux, auto mocking LCD")
            return False
        if (self._xconfig.get("lcd.mock", True)):
            self._xlog.warning("Mocking LCD by Config")
            return False
        return True
    
    def clear(self):
        """
        Clear the LCD display
        """
        self.driver.clear()

    def test(self):
        logging.info("LCD test")

        logging.basicConfig(level=logging.DEBUG)
        try:
            # display with hardware SPI:
            ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
            #disp = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
            # self.driver = LCD_2inch()
            # Initialize library.
            self.driver.Init()
            # Clear display.
            self.driver.clear()
            #Set the backlight to 100
            self.driver.bl_DutyCycle(50)

            # Create blank image for drawing.
            image1 = Image.new("RGB", (self.driver.height, self.driver.width ), "WHITE")
            draw = ImageDraw.Draw(image1)

            logging.info("draw point")

            draw.rectangle((5,10,6,11), fill = "BLACK")
            draw.rectangle((5,25,7,27), fill = "BLACK")
            draw.rectangle((5,40,8,43), fill = "BLACK")
            draw.rectangle((5,55,9,59), fill = "BLACK")

            logging.info("draw line")
            draw.line([(20, 10),(70, 60)], fill = "RED",width = 1)
            draw.line([(70, 10),(20, 60)], fill = "RED",width = 1)
            draw.line([(170,15),(170,55)], fill = "RED",width = 1)
            draw.line([(150,35),(190,35)], fill = "RED",width = 1)

            logging.info("draw rectangle")
            draw.rectangle([(20,10),(70,60)],fill = "WHITE",outline="BLUE")
            draw.rectangle([(85,10),(130,60)],fill = "BLUE")

            logging.info("draw circle")
            draw.arc((150,15,190,55),0, 360, fill =(0,255,0))
            draw.ellipse((150,65,190,105), fill = (0,255,0))

            logging.info(f"set font in {self.FONT_PATH}")
            Font1 = ImageFont.truetype(os.path.join(self.FONT_PATH, "Font01.ttf"),25)
            Font2 = ImageFont.truetype(os.path.join(self.FONT_PATH, "Font01.ttf"),35)
            Font3 = ImageFont.truetype(os.path.join(self.FONT_PATH, "Font02.ttf"),32)

            logging.info("draw text")
            draw.rectangle([(0,65),(140,100)],fill = "WHITE")
            draw.text((5, 68), 'Hello world', fill = "BLACK",font=Font1)
            draw.rectangle([(0,115),(190,160)],fill = "RED")
            draw.text((5, 118), 'WaveShare', fill = "WHITE",font=Font2)
            draw.text((5, 160), '1234567890', fill = "GREEN",font=Font3)
            text= u"微雪电子"
            draw.text((5, 200),text, fill = "BLUE",font=Font3)

            logging.info("Rotate image")
            image1=image1.rotate(180)
            logging.info("Show image")
            self.driver.ShowImage(image1)
            time.sleep(3)
            logging.info("show image")
            image = Image.open(os.path.join(self.PIC_PATH, "LCD_2inch.jpg"))
            image = image.rotate(180)
            self.driver.ShowImage(image)
            time.sleep(3)
            self.driver.module_exit()
            logging.info("quit:")
        except IOError as e:
            logging.info(e)    
        except KeyboardInterrupt:
            self.driver.module_exit()
            return