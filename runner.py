import os
from dotenv import load_dotenv
import importlib.metadata
import logging

from pyxavi import TerminalColor, Config, Logger, Dictionary, full_stack

from kleine.lib.utils.config_loader import ConfigLoader
# from kleine.test import Test

from definitions import ROOT_DIR, CONFIG_DIR

from kleine.main import Main


def load_environment():
    """
    Loads the environment

    This means to load the environment vars from the .env file and also
    any other parameter related to the environment.
    """
    load_dotenv()


def load_logger(config: Config, loglevel: int = None) -> logging:

    if loglevel is not None:
        # Lets first merge the config with the new value
        logger_config = config.get("logger")
        logger_config["loglevel"] = loglevel
        logger_config["stdout"]["active"] = True
        config.merge_from_dict(parameters={"logger": logger_config})

    return Logger(config=config, base_path=ROOT_DIR).get_logger()

def run():
    try:
        # Instantiating
        load_environment()
        config = ConfigLoader.load_config_files()
        logger = load_logger(config=config)
        parameters = Dictionary({
            "base_path": ROOT_DIR,
            "app_version": importlib.metadata.version('kleine')
        })

        # Delegate the run to Main
        logger.debug("Starting Main run")
        main = Main(config=config, params=parameters)
        main.run()
        logger.info("End of the Main run")


    except RuntimeError as e:
        print(TerminalColor.RED_BRIGHT + str(e) + TerminalColor.END)
    except Exception:
        print(full_stack()) 

def _initialize():
    load_environment()
    config = ConfigLoader.load_config_files()
    logger = load_logger(config=config)
    parameters = Dictionary({
        "base_path": ROOT_DIR,
        "app_version": importlib.metadata.version('kleine')
    })

    return config, logger, parameters

if __name__ == '__main__':
    run()