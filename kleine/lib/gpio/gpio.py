from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .mocked_gpiozero import MockedButton

class Gpio(PyXavi):

    # GPIO pin definitions, not physical pin numbers
    YELLOW_BUTTON_PIN = (16, "space")  # GPIO16, emulated with 'space' key
    GREEN_BUTTON_PIN = (6, "enter")  # GPIO6, emulated with 'enter' key

    yellow_button: MockedButton = None
    green_button: MockedButton = None

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Gpio, self).init_pyxavi(config=config, params=params)

        # Initialise GPIO buttons
        self._xlog.info("Initialising GPIO buttons...")
        self.yellow_button = self._new_button(self.YELLOW_BUTTON_PIN)
        self.green_button = self._new_button(self.GREEN_BUTTON_PIN)

    def is_yellow_button_pressed(self) -> bool:
        return self.yellow_button.is_pressed
    
    def is_green_button_pressed(self) -> bool:
        return self.green_button.is_pressed

    def _new_button(self, pin: tuple) -> MockedButton:
        if self._xconfig.get("gpio.mock", False):
            self._xlog.warning(f"Creating mocked button for pin {pin[0]} with key binding '{pin[1]}'")
            return MockedButton(pin[0], keyboard_key_binding_to=pin[1], config=self._xconfig, params=self._xparams)
        else:
            self._xlog.debug(f"Creating real button for pin {pin[0]}")
            from gpiozero import Button

            return Button(pin[0])
