from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from .mocked_gpiozero import MockedButton

class Gpio(PyXavi):

    buttons: dict = {}

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Gpio, self).init_pyxavi(config=config, params=params)

        # Initialise GPIO buttons
        self._xlog.info("Initialising GPIO buttons...")

        # Initialise buttons
        self.initialize_buttons()

    def initialize_buttons(self):

        # Gather the definitions from the config
        button_definitions = self._xconfig.get("gpio.buttons", [])
        for button in button_definitions:
            self.buttons[button["name"]] = self._new_button(button["pin"], button["mocked_as"])

    def is_button_pressed(self, button_name: str) -> bool:
        if button_name not in self.buttons:
            self._xlog.error(f"Button '{button_name}' not defined")
            raise KeyError(f"Button '{button_name}' not defined")
        return self.buttons[button_name].is_pressed

    def _new_button(self, pin: int, mocked_as: str) -> MockedButton:
        if self._xconfig.get("gpio.mock", False):
            self._xlog.warning(f"Creating mocked button for pin {pin} with key binding '{mocked_as}'")
            return MockedButton(pin, keyboard_key_binding_to=mocked_as, config=self._xconfig, params=self._xparams)
        else:
            self._xlog.debug(f"Creating real button for pin {pin}")
            from gpiozero import Button

            return Button(pin)
