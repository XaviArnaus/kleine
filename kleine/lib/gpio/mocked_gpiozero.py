from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

# class MockedGpiozero(PyXavi):
#     """
#     Mocked version of gpiozero library for non-Linux systems or testing purposes.
#     """

#     def __init__(self, config: Config = None, params: Dictionary = None):
#         super(MockedGpiozero, self).init_pyxavi(config=config, params=params)
#         self._xlog.info("Initialized MockedGpiozero for testing purposes.")

class MockedButton(PyXavi):
    """
    Mocked version of gpiozero.Button for testing purposes.
    """

    pin: int = None
    key_to_emulate_pin: str = None
    _is_pressed: bool = False
    _listener = None

    def __init__(self, pin: int, keyboard_key_binding_to: str = "space", config: Config = None, params: Dictionary = None):
        super(MockedButton, self).init_pyxavi(config=config, params=params)

        self.pin = pin
        if keyboard_key_binding_to is None:
            keyboard_key_binding_to = "space"
        self._is_pressed = False

        self._make_binding(keyboard_key_binding_to)

    @property
    def is_pressed(self) -> bool:
        value = self._is_pressed
        if value:
            self._is_pressed = False  # Reset after reading
        return value

    def _on_press(self, key):
        if key == self.key_to_emulate_pin:
            self._xlog.debug(f"Mocking GPIO: {self.key_to_emulate_pin} key (meaning pin {self.pin}) was PRESSED")
            self._is_pressed = True

    def _make_binding(self, key_binding: str):
        '''
        Internal method to create keyboard binding for mocking the button press.
        Currently not used as we check the key state directly in is_pressed property.
        '''
        from pynput import keyboard

        if key_binding == "space":
            self.key_to_emulate_pin = keyboard.Key.space
        elif key_binding == "enter":
            self.key_to_emulate_pin = keyboard.Key.enter
        elif key_binding == "esc":
            self.key_to_emulate_pin = keyboard.Key.esc
        else:
            self.key_to_emulate_pin = key_binding

        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
    
    def close(self):
        if self._listener is not None:
            self._listener.stop()