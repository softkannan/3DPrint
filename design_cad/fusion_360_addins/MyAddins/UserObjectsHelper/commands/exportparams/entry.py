#!/usr/bin/env python
"""

This module supports the insert objects command feature

This module uses the icons from <a href="https://www.flaticon.com/free-icons/formula" title="formula icons">Formula icons created by Smashicons - Flaticon</a>

"""
__author__ = "SoftK"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

import json
import adsk.core
import adsk.fusion
import traceback
import os
import csv
import sys
import io
import math
from pathlib import Path
from ...lib import fusion360utils as futil
from ... import config
from datetime import datetime

app = adsk.core.Application.get()
ui = app.userInterface

# TODO ********************* Change these names *********************
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}__insert_predef_objects'
CMD_NAME = 'Export Params'
CMD_Description = 'Exports User Params to CSV file'
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'
TOOLBARPANELS = ["InsertPanel"]

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create a command Definition.
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

        # Add command created handler. The function passed here will be executed when the command is executed.
        futil.add_handler(cmd_def.commandCreated, command_created)

        # Adds the commandDefinition to the toolbar
        for panel in TOOLBARPANELS:
            control = ui.allToolbarPanels.itemById(
                panel).controls.addCommand(cmd_def)
            # Specify if the command is promoted to the main toolbar.
            control.isPromoted = IS_PROMOTED

    except:
        futil.log(f'{CMD_NAME} Command Start Event {traceback.format_exc()}')


# Executed when add-in is stopped.
def stop():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Removes the commandDefinition from the toolbar
        for panel in TOOLBARPANELS:
            p = ui.allToolbarPanels.itemById(panel).controls.itemById(CMD_ID)
            if p:
                p.deleteMe()

        # Deletes the commandDefinition
        ui.commandDefinitions.itemById(CMD_ID).deleteMe()
    except:
        futil.log(f'{CMD_NAME} Command Stop Event {traceback.format_exc()}')


# Event handler that is called when the user clicks the command button in the UI.
# To have a dialog, you create the desired command inputs here. If you don't need
# a dialog, don't create any inputs and the execute event will be immediately fired.
# You also need to connect to any command related events here.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')
    doExport()

def doExport():
     app = adsk.core.Application.get()
     ui  = app.userInterface
     
     try:   
         fileDialog = ui.createFileDialog()
         fileDialog.isMultiSelectEnabled = False
         fileDialog.title = "Get the file to save the parameters to"
         fileDialog.filter = 'Text files (*.csv)'
         fileDialog.filterIndex = 0
         fileDialog.initialDirectory = config.STARTING_FOLDER
         
         dialogResult = fileDialog.showSave()
             
         if dialogResult == adsk.core.DialogResults.DialogOK:
             filename = fileDialog.filename
         else:
             return

         writeParametersToFile(filename)

     except:
         if ui:
             ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 


def writeParametersToFile(filePath):
    app = adsk.core.Application.get()
    design = app.activeProduct
                      
    with open(filePath, 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, dialect=csv.excel)
        csvWriter.writerow(['Name', 'Value', 'Units', 'Comments']) 
        for param in design.allParameters:
            try:
                paramUnit = param.unit
            except:
                paramUnit = ""
            
            csvWriter.writerow([param.name, param.expression, paramUnit, param.comment]) 
    
    # get the name of the file without the path    
    partsOfFilePath = filePath.split("/")
    ui  = app.userInterface
    ui.messageBox('Parameters written to ' + partsOfFilePath[-1])       
   
