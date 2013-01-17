# -*- coding: utf-8 -*-

#                  ____  _         __      ___
#                 |  _ \| |        \ \    / (_)
#      _ __  _   _| |_) | |_   _  __\ \  / / _  __ _
#     | '_ \| | | |  _ <| | | | |/ _ \ \/ / | |/ _` |
#     | |_) | |_| | |_) | | |_| |  __/\  /  | | (_| |
#     | .__/ \__, |____/|_|\__,_|\___| \/   |_|\__,_|
#     | |     __/ |
#     |_|    |___/
#


"""
pyBlueVia: A Python wrapper around the BlueVia API.

More info about BlueVia at http://bluevia.com

:copyright: (c) 2013 by Jose Antonio Rodríguez.
:license: MIT, see LICENSE for more details.

"""

__title__ = 'pyBlueVia'
__version__ = '0.1.0'
__author__ = 'Jose Antonio Rodríguez'
__email__ = 'jarf1975@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Jose Antonio Rodríguez'


from .api import Api
from .api import SMS_MT, MMS_MT
from .exceptions import *

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


def add_stderr_logger(level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.

    Returns the handler after adding it.
    """
    # This method needs to be in this __init__.py to get the __name__ correct
    # even if pyBlueVia is vendored within another package.
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added an stderr logging handler to logger: {0}'.format(__name__))
    return handler
