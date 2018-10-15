# -*- coding:utf-8 -*-
import logging.config
from ..config.Config import LOGGING_CONFIG, DEBUG_MODE


class LogUtil:
    """
    日志记录工具
    """

    def __init__(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        if DEBUG_MODE:
            self.__logger = logging.getLogger("debug")
        else:
            self.__logger = logging.getLogger()

    def error(self, msg):
        self.__logger.error(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def debug(self, msg):
        self.__logger.debug(msg)

    def warning(self, msg):
        self.__logger.warning(msg)
