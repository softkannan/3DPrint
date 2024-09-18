#!/usr/bin/env python
"""

entry point for fusion 360 addin

"""
__author__ = "SoftK"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

from . import commands
from .lib import fusion360utils as futil

# Called at the start of the addin
def run(context):
    try:
        # This will run the start function in each of the commands as defined in commands/__init__.py
        commands.start()

    except:
        futil.handle_error('run')

# called at stop of the addin
def stop(context):
    try:
        # Remove all of the event handlers app has created
        futil.clear_handlers()

        # This will run the stop function in each of the commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')