from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from gpiozero import Button

class Gpio(PyXavi):

    # GPIO pin definitions, not physical pin numbers
    YELLOW_BUTTON_PIN = 16
    GREEN_BUTTON_PIN = 12

    yellow_button: Button = None
    green_button: Button = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Gpio, self).init_pyxavi(config=config, params=params)

        # Initialise GPIO buttons
        self._xlog.info("Initialising GPIO buttons...")
        self.yellow_button = Button(self.YELLOW_BUTTON_PIN)
        self.green_button = Button(self.GREEN_BUTTON_PIN)
    
    def is_yellow_button_pressed(self) -> bool:
        return self.yellow_button.is_pressed
    
    def is_green_button_pressed(self) -> bool:
        return self.green_button.is_pressed
