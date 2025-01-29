#!/usr/bin/env python
"""

define the commands that will be added to your add-in.

"""
__author__ = "SoftK"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

# Import the modules corresponding to the commands 
# If you want to add an additional command, duplicate one of the existing directories and import it here.
# You need to use aliases (import "entry" as "my_module") assuming you have the default module named "entry".
from .commandDialog import entry as commandDialog
from .exportparams import entry as exportparams
from .insertparams import entry as insertparams

# add your imported modules to this list.
# Fusion will automatically call the start() and stop() functions.
commands = [
#    commandDialog,
    insertparams,
    exportparams
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()