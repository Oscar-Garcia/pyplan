# -*- coding: utf-8 -*-
import logging
from .config import DEFAULT_LOGGING_LEVEL


def get_default_logger():
    """
    Gets the default Python logger.
    """
    logging.basicConfig(level=DEFAULT_LOGGING_LEVEL)
    return logging.getLogger('PyPlan')
