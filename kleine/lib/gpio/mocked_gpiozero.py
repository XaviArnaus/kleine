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
    is_pressed: bool = False

    def __init__(self, pin: int, keyboard_key_binding_to: str = "space", config: Config = None, params: Dictionary = None):
        super(MockedButton, self).init_pyxavi(config=config, params=params)

        self.pin = pin
        self.key_to_emulate_pin = keyboard_key_binding_to
        self._is_pressed = False

    @property
    def is_pressed(self) -> bool:
        return self._is_keyboard_key_pressed()

    # def press(self):
    #     self._is_pressed = True

    # def release(self):
    #     self._is_pressed = False
    
    def _is_keyboard_key_pressed(self) -> bool:
        '''
        Internal method to check if the space key is pressed on the keyboard.
        Used for mocking the mute switch when GPIO is not available.

        https://github.com/boppreh/keyboard
        '''
        import keyboard  # Imported here to avoid issues on systems without keyboard module

        # is_pressed = keyboard.is_pressed('space')
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed(self.key_to_emulate_pin):  # if key 'space' is pressed
                self._xlog.debug(f"Mocking GPIO: {self.key_to_emulate_pin} key (meaning pin {self.pin}) is PRESSED")
                return True
            elif keyboard.is_pressed('control+c'):  # to allow exit from program
                self._xlog.debug("Exiting due to Ctrl+C")
                raise KeyboardInterrupt()
        except KeyboardInterrupt as e:
            raise e
        except:
            pass  # if user pressed a key other than the given key the loop will break
        return False