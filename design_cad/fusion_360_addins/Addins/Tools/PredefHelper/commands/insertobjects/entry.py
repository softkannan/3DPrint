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
CMD_NAME = 'Insert Objects'
CMD_Description = 'Insert Predefined User Objects'
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

    # Create the event handlers you will need for this instance of the command
    futil.add_handler(args.command.execute, command_execute,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged,
                      command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview,
                      command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy,
                      local_handlers=local_handlers)

    # Create the user interface for your command by adding different inputs to the CommandInputs object
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # ******************************** Define your UI Here ********************************
    if len(config.g_UserObjects) == 0:
        currentFolder = os.path.dirname(__file__)
        resourcesPath = 'G:\\github\\3DPrint\\design_calibration\\MyAddins\\PreDefUserObjects'
        if os.path.exists(resourcesPath) == False:
            resourcesPath = os.path.abspath(
                os.path.join(currentFolder, '../../PreDefUserObjects/'))

        idCount = 0
        for name in os.listdir(resourcesPath):
            folderName = os.path.join(resourcesPath, name)
            if os.path.isdir(folderName):
                curFolderMap = {}
                for filename in os.listdir(folderName):
                    if filename.lower().endswith('.f3d'):
                        fullfilename = os.path.abspath(
                            os.path.join(folderName, filename))
                        displayname = Path(fullfilename).stem
                        curFolderMap[displayname] = fullfilename

                ddFileItemID = "DDFileItem" + str(idCount)
                idCount += 1
                config.g_UserObjects[name] = (curFolderMap, ddFileItemID)

    ddFolderType = inputs.addDropDownCommandInput(
        "DDFolderType", "Select Folder", adsk.core.DropDownStyles.TextListDropDownStyle)

    for dirName in config.g_UserObjects:
        ddFolderType.listItems.add(dirName, False, '')
        curFolderMap, ddFileItemID = config.g_UserObjects[dirName]
        ddFileItem = inputs.addDropDownCommandInput(
            ddFileItemID, "Select File", adsk.core.DropDownStyles.TextListDropDownStyle)
        for fileName in curFolderMap:
            ddFileItem.listItems.add(fileName, False, '')
        if ddFileItemID != "DDFileItem0":
            ddFileItem.isVisible = False

# insert given CAd file to current document
def insertCADObject(filename):
    # Get application import manager
    importManager = app.importManager
    # Get active design
    design = app.activeProduct
    # Get root component
    rootComp = design.rootComponent
    archiveOptions = importManager.createFusionArchiveImportOptions(filename)
    # Import archive file to root component
    importManager.importToTarget2(archiveOptions, rootComp)

# This function will be called when the user hits the OK button in the command dialog


def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug
    futil.log(f'{CMD_NAME} Command Execute Event')
    try:
        inputs = args.command.commandInputs
        folderName = inputs.itemById("DDFolderType").selectedItem.name
        if len(folderName) > 0:
            curFolderMap, ddFileItemID = config.g_UserObjects[folderName]
            fileName = inputs.itemById(ddFileItemID).selectedItem.name
            if len(fileName) > 0:
                fileAbsName = curFolderMap[fileName]
                insertCADObject(fileAbsName)
    except:
        pass

    # # Get a reference to your command's inputs
    # text_input: adsk.core.TextBoxCommandInput = inputs.itemById('text_input')
    # value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    # # Construct a message
    # message_action = 'updateMessage'
    # message_data = {
    #     'myValue': f'{value_input.value} cm',
    #     'myExpression': value_input.expression,
    #     'myText': text_input.formattedText
    # }
    # # JSON strings are a useful way to translate between javascript objects and python dictionaries
    # message_json = json.dumps(message_data)

# This function will be called when the command needs to compute a new preview in the graphics window


def command_preview(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    futil.log(f'{CMD_NAME} Command Preview Event')


# This function will be called when the user changes anything in the command dialog
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    if changed_input.id == "DDFolderType":
        folderName = args.input.selectedItem.name
        for name in config.g_UserObjects:
            curFolderMap, ddFileItemID = config.g_UserObjects[name]
            args.inputs.itemById(ddFileItemID).isVisible = False
        curFolderMap, ddFileItemID = config.g_UserObjects[folderName]
        args.inputs.itemById(ddFileItemID).isVisible = True

        # This event handler is called when the command terminates.


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f'{CMD_NAME} Command Destroy Event')
