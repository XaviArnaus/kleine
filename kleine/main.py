from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from definitions import ROOT_DIR


class Main(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

    async def run(self):

        self._xlog.info("🚀 Starting Kleine main run...")

        # --- Your main application logic goes here ---

        #Test().run()

        # However it happened, just close nicely.
        self.close_nicely()
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely...")
