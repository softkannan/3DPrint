#!/usr/bin/env python
"""

This module inserts user selected csv file user parameters to fusion 360 current document

This module uses the icons from <a href="https://www.flaticon.com/free-icons/construction-and-tools" title="construction and tools icons">Construction and tools icons created by Vectorslab - Flaticon</a>

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
# from . import csvhelperutil
from . import userparam

app = adsk.core.Application.get()
ui = app.userInterface

# ********************* Change these names *********************
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_insert_predef_params'
CMD_NAME = 'Import'
CMD_Description = 'Imports CSV User Params / Imports Object file'
IS_PROMOTED = True

# *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
# TOOLBARPANELS = ["SolidCreatePanel"]
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
    doImport()
   

# import CSV file and create user parameters
def importCSVFile(filePath):
    # ['Name;Value;Units;Comments']
    print("Start to read CSV, " + filePath)
    csvKeysToCheck = ['Name', 'Value', 'Units', 'Comments']
    file = open(filePath, 'r')
    csv_Dictionary = csv.DictReader(file)
    headers = csv_Dictionary.fieldnames
    if headers != csvKeysToCheck:
        print("Error: - csv file doesn't contain all necessary keys")
        original = ', '.join([str("'"+elem+"'")
                              for elem in csvKeysToCheck])
        current = ', '.join([str("'"+elem+"'") for elem in headers])
        print("\t original:\t" + original)
        print("\t current:\t" + current)
        return False

    print("Start to update Fusion360 user parameters")
    fusionParameters = userparam.Fusion360UserParameters()
    for row in csv_Dictionary:
        csvRow = dict(row)
        name = csvRow["Name"]
        value = csvRow["Value"]
        units = csvRow["Units"]
        comments = csvRow["Comments"]
        fusionParameters.updateFusionUserParameters(
            name, value, units, comments)
    print(str(csv_Dictionary.line_num) + " parameters where updated")

def doImport():
     app = adsk.core.Application.get()
     ui  = app.userInterface
     
     try:   
         fileDialog = ui.createFileDialog()
         fileDialog.isMultiSelectEnabled = False
         fileDialog.title = "Get the file to read user parameters"
         fileDialog.filter = 'Supported Files(*.csv;*.step;*.f3d);;All files (*.*)'
         fileDialog.filterIndex = 0
         fileDialog.initialDirectory = config.STARTING_FOLDER
         
         dialogResult = fileDialog.showOpen()
             
         if dialogResult == adsk.core.DialogResults.DialogOK:
             filename = fileDialog.filename
         else:
             return
         
         if filename.endswith(".csv"):
             # if isImport is true read the parameters from a file
             importCSVFile(filename)
         else:
             insertCADObject(filename)
        

     except:
         if ui:
             ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 

def updateParameter(design, paramsList, row):
    # get the values from the csv file.
    try:
        nameOfParam = row[0].strip()
        unitOfParam = row[1].strip()
        expressionOfParam = row[2].strip()
        try:
            commentOfParam = row[3].strip()
        except:
            commentOfParam = ''
    except Exception as e:
        print(str(e))
        # no plint to retry
        return True

    # userParameters.add did not used to like empty string as comment
    # so we make it a space
    # comment might be missing
    #if commentOfParam == '':
    #    commentOfParam = ' ' 

    try: 
        # if the name of the paremeter is not an existing parameter add it
        if nameOfParam not in paramsList:
            valInputparam = adsk.core.ValueInput.createByString(expressionOfParam) 
            design.userParameters.add(nameOfParam, valInputparam, unitOfParam, commentOfParam)
            print("Added {}".format(nameOfParam))
            
        # update the values of existing parameters            
        else:
            paramInModel = design.allParameters.itemByName(nameOfParam)
            #paramInModel.unit = unitOfParam
            paramInModel.expression = expressionOfParam
            paramInModel.comment = commentOfParam
            print("Updated {}".format(nameOfParam))
        
        return True

    except Exception as e:
        print(str(e))
        print("Failed to update {}".format(nameOfParam))
        return False

def readParametersFromFile(filePath):
    app = adsk.core.Application.get()
    design = app.activeProduct
    ui  = app.userInterface
    try:
        paramsList = []
        for oParam in design.allParameters:
            paramsList.append(oParam.name) 

        retryList = []            
        
        # read the csv file.
        with open(filePath) as csvFile:
            csvReader = csv.reader(csvFile, dialect=csv.excel)
            for row in csvReader:
                # if the parameter is referencing a non-existent
                # parameter then  this will fail
                # so let's store those params and try to add them in the next round 
                if not updateParameter(design, paramsList, row):
                    retryList.append(row)

        # let's keep going through the list until all is done
        count = 0
        while len(retryList) + 1 > count:
            count = count + 1
            for row in retryList:
                if updateParameter(design, paramsList, row):
                    retryList.remove(row)
                
        if len(retryList) > 0:
            params = ""
            for row in retryList:
                params = params + '\n' + row[0]

            ui.messageBox('Could not set the following parameters:' + params)
        else:
            ui.messageBox('Finished reading and updating parameters')
    except:
        if ui:
            ui.messageBox('AddIn Stop Failed:\n{}'.format(traceback.format_exc()))

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