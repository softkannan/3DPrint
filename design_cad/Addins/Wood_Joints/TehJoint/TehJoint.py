from . import config
import os
import adsk.core
#from .lib import fusion360utils as futil

from .Joints import Joints

import traceback
import time

app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Teh Joint'
CMD_Description = 'Add-in for easy Jointing'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'AssemblePanel'
# COMMAND_BESIDE_ID = 'ScriptsManagerCommand'
COMMAND_BESIDE_ID = ''

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'resources', '')


# global set of event handlers to keep them referenced for the duration of the command
handlers = []
ButtonDefinition = None

# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = True


def run(context):
    try:
        print('run')
        addButton(ICON_FOLDER)
    except Exception as e:
        if ui:
            ui.messageBox(f'AddIn Run Failed: {e}')


def stop(context):
    #ui = None
    try:
        print('stop')
        removeButton()
    except Exception as e:
        if ui:
            ui.messageBox(f'AddIn Stop Failed: {e}')


def addButton(folder):
    # stop(context)
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        print(cmd_def)
        # cmd_def.deleteMe()

    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description, folder)
    global ButtonDefinition
    ButtonDefinition = cmd_def

    # Define an event handler for the command created event. It will be called when the button is clicked.
    #futil.add_handler(cmd_def.commandCreated, command_created)

    on_command_created = CommandCreatedHandler()
    cmd_def.commandCreated.add(on_command_created)
    handlers.append(on_command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar.
    control.isPromoted = IS_PROMOTED

def removeButton():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()        

def getInputValues(args):
    command = args.firingEvent.sender
    inputs = command.commandInputs
    values = {}
    for input in inputs:
        if hasattr(input, 'value'):
            values[input.id] = input.value
        elif hasattr(input, 'listItems'):
            for listItem in input.listItems:
                if listItem.isSelected:
                    values[input.id] = listItem.name
        elif hasattr(input, 'selection'):
            values[input.id] = []
            for j in range(0, input.selectionCount):
                values[input.id].append(input.selection(j))
    return values

def getInputByName(args, name):
    command = args.firingEvent.sender
    inputs = command.commandInputs        
    return inputs.itemById(name)

class CommonCommandEventHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()    
        self.app = app
        self.ui = self.app.userInterface

    def getInputValues(self, args):
        return getInputValues(args)

    def getInput(self, args, name):
        return getInputByName(args, name)
        
class CommandExecuteHandler(CommonCommandEventHandler):
    def __init__(self):
        super().__init__()
  

    def notify(self, args):
        # print('CommandExecuteHandler')
        try:
            values = self.getInputValues(args)
            with Joints(app) as joints:
                joints.makeJoints(
                    values['srcComponentSelection'], 
                    values['jointSelection'],
                    values['offset'],
                    values['angle'],
                    values['flip'],
                    values['hideJoints'],
                    )
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandPreviewHandler(CommonCommandEventHandler):
    def __init__(self):
        super().__init__()
  

    def notify(self, args):
        # print('CommandPreviewHandler')

        eventArgs = adsk.core.CommandEventArgs.cast(args)
        try:
            values = self.getInputValues(args)

            if not values['previewActive']:
                eventArgs.isValidResult = False
                return


            # if values['srcComponentSelection'] and values['jointSelection']:
            #     geo0 = adsk.fusion.JointGeometry.createByPoint(values['srcComponentSelection'][0].entity)
            #     # geo1 = adsk.fusion.JointGeometry.createByPoint(values['jointSelection'][0].entity)
            #     geo1 = values['jointSelection'][0].entity
                
            #     # Create joint input

            #     self.product = self.app.activeProduct
            #     self.design = adsk.fusion.Design.cast(self.product)
            #     self.rootComp = self.design.rootComponent              
            #     joints = self.rootComp.joints

            #     jointInput = joints.createInput(geo0, geo1)            
            #     jointInput.setAsRigidJointMotion()

            #     joints.add(jointInput)

            # return

            if values['srcComponentSelection'] and values['jointSelection']:
                with Joints(app) as joints:

                    joints.makeJoints(
                        values['srcComponentSelection'], 
                        values['jointSelection'],
                        values['offset'],
                        values['angle'],
                        values['flip'],
                        values['hideJoints'],
                        )

            # IF Set the isValidResult property to use these results at the final result. THEN the execute event not being fired.
            eventArgs.isValidResult = True                
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # if args.input.id == 'dstComponentSelection':
            #     if args.input.selectionCount > 0:
            #         getInputByName(args, 'srcComponentSelection').hasFocus = True

            if args.input.id == 'srcComponentSelection':
                if args.input.selectionCount > 0:
                    getInputByName(args, 'jointSelection').hasFocus = True

            elif args.input.id == 'jointSelection':
                values = getInputValues(args)
                if not values['jointSelection']:
                    return
                return
                Rotate =  getInputByName(args, 'angle')
                lastSelection = values['jointSelection'][len(values['jointSelection'])-1]
                Rotate.setManipulator(lastSelection.entity.geometry.center, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            print('CommandDestroyHandler')

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            # adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            command = args.command
            command.isRepeatable = False

            # cmd.helpFile = 'help.html'

            # define the inputs
            inputs = command.commandInputs

            inputs.addImageCommandInput('image', '', 'resources/Icon_128.png')


            # dstComponentSelection = inputs.addSelectionInput('dstComponentSelection', 'Dst Component',
            #                                           'Select Component for store new components and joints')
            # dstComponentSelection.setSelectionLimits(1,1)
            # dstComponentSelection.addSelectionFilter('Occurrences')


            selectionInputComponent = inputs.addSelectionInput('srcComponentSelection', 'Select Joint Origin',
                                                      'Select Component with Joint Origin (or Select Joint Origin)')
            selectionInputComponent.setSelectionLimits(1,1)
            selectionInputComponent.addSelectionFilter('Occurrences')
            selectionInputComponent.addSelectionFilter('JointOrigins')
            # selectionInputComponent.addSelectionFilter('Vertices')
            # selectionInputComponent.addSelectionFilter('CircularEdges')


            selectionInputJoints = inputs.addSelectionInput('jointSelection', 'Select Joins',
                                                      'Select origins to join')
            selectionInputJoints.setSelectionLimits(0)
            # selectionInputJoints.addSelectionFilter('JointOrigins')
            # selectionInputJoints.addSelectionFilter('SketchPoints')
            # selectionInputJoints.addSelectionFilter('ConstructionPoints')
            # selectionInputJoints.addSelectionFilter('Vertices')
            selectionInputJoints.addSelectionFilter('CircularEdges')
            selectionInputJoints.addSelectionFilter('JointOrigins')

            # Create float spinner input.
            inputs.addFloatSpinnerCommandInput('offset', 'Offset', 'mm', -1000 , 1000, 1, 0)

            Rotate = inputs.addAngleValueCommandInput('angle', 'Angle', adsk.core.ValueInput.createByString('0 degree'))
            #Rotate.setManipulator(adsk.core.Point3D.create(100, 100, 0), adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 0, 1))

            inputs.addBoolValueInput('flip', 'Flip', True)
            inputs.addBoolValueInput('hideJoints', 'Hide Joints', True)
            
            inputs.addBoolValueInput('previewActive', 'Preview', True, "", True)

            onInputChanged = InputChangedHandler()
            command.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            onExecute = CommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)

            onExecutePreview = CommandPreviewHandler()
            command.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)

            onDestroy = CommandDestroyHandler()
            command.destroy.add(onDestroy)
            handlers.append(onDestroy)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
