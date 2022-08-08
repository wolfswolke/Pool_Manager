"""
"""

# --------------------------------------- #
#               imports                   #
# --------------------------------------- #
from gutils.config_handle import config
from gutils.logging_handle import logger

# --------------------------------------- #
#              definitions                #
# --------------------------------------- #
MODULE_LOGGER_HEAD = "start_app -> "
APP_VERSION = "v01-00-00"


# --------------------------------------- #
#              global vars                #
# --------------------------------------- #


# --------------------------------------- #
#              functions                  #
# --------------------------------------- #
def setup_logging(level):
    logger.set_logging_level(level)
    logger.set_cmd_line_logging_output()


# --------------------------------------- #
#               classes                   #
# --------------------------------------- #


# --------------------------------------- #
#                main                     #
# --------------------------------------- #
if __name__ == "__main__":
    try:
        config.load_config("../config/Name_config.yml")
        config.set_element("general", "version", APP_VERSION)

        setup_logging(config.get_element("general", "debug_level"))

        logger.info("-----------------------------------------------------------")
        logger.info("            Started System {}".format(APP_VERSION))
        logger.info("-----------------------------------------------------------")

        

    except KeyboardInterrupt:
        influx_db.stop_influx_upload()
        logger.info("-----------------------------------------------------------")
        logger.info("            System Stopped")
        logger.info("-----------------------------------------------------------")
