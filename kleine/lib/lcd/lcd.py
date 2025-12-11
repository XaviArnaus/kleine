#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from .LCD_2inch import LCD_2inch
from PIL import Image,ImageDraw,ImageFont

from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class Lcd(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Lcd, self).init_pyxavi(config=config, params=params)

        # Initialise the LCD display
        self._xlog.info("Initialising LCD display...")
        self.lcd = LCD_2inch()

    def get_lcd(self) -> LCD_2inch:
        return self.lcd
    
    def test(self):
        logging.info("LCD test")

        # Raspberry Pi pin configuration:
        RST = 27
        DC = 25
        BL = 18
        bus = 0 
        device = 0 
        logging.basicConfig(level=logging.DEBUG)
        try:
            # display with hardware SPI:
            ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
            #disp = LCD_2inch.LCD_2inch(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
            # self.lcd = LCD_2inch()
            # Initialize library.
            self.lcd.Init()
            # Clear display.
            self.lcd.clear()
            #Set the backlight to 100
            self.lcd.bl_DutyCycle(50)

            # Create blank image for drawing.
            image1 = Image.new("RGB", (self.lcd.height, self.lcd.width ), "WHITE")
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

            logging.info("set font")
            Font1 = ImageFont.truetype("Font/Font01.ttf",25)
            Font2 = ImageFont.truetype("Font/Font01.ttf",35)
            Font3 = ImageFont.truetype("Font/Font02.ttf",32)

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
            self.lcd.ShowImage(image1)
            time.sleep(3)
            logging.info("show image")
            image = Image.open('pic/LCD_2inch4_1.jpg')	
            image = image.rotate(180)
            self.lcd.ShowImage(image)
            time.sleep(3)
            self.lcd.module_exit()
            logging.info("quit:")
        except IOError as e:
            logging.info(e)    
        except KeyboardInterrupt:
            self.lcd.module_exit()
            logging.info("quit:")
            exit()