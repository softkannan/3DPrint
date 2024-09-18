import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
from . import logic


app = adsk.core.Application.get()
ui = app.userInterface

resizer_modifier_logic: logic.ResizerModifierLogic = None

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Object Resizer'
CMD_Description = 'Object Resizer can be used to resize an object using dimensional values instead of scale factor.'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

units="mm"

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidModifyPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'
PALETTE_ID = config.sample_palette_id

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    ui.messageBox("The Object Resizer add-in has added a new command to the MODIFY panel in the SOLID tab of the DESIGN workspace.")
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    palette = ui.palettes.itemById(PALETTE_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()
    
    # Delete the Palette
    if palette:
        palette.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs
    
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)
    futil.add_handler(args.command.select, command_select, local_handlers=local_handlers)
    futil.add_handler(args.command.unselect, command_unselect, local_handlers=local_handlers)
    futil.add_handler(args.command.preSelectStart, command_pre_select_start, local_handlers=local_handlers)
    futil.add_handler(args.command.preSelectEnd, command_pre_select_stop, local_handlers=local_handlers)

    des: adsk.fusion.Design = app.activeProduct
    if des is None:
        return

    # Create an instance of the Spur Gear command class.
    global resizer_modifier_logic
    resizer_modifier_logic = logic.ResizerModifierLogic(des)

    args.command.isExecutedWhenPreEmpted = False
    resizer_modifier_logic.create_command_inputs(inputs)

   

def command_unselect(args: adsk.core.InputChangedEventArgs):
    resizer_modifier_logic.handle_unselection_event(args)

def command_select(args: adsk.core.InputChangedEventArgs):
    resizer_modifier_logic.handle_selection_event(args)
    
def command_execute(args: adsk.core.CommandEventArgs):
   resizer_modifier_logic.handle_execute(args)
    
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    resizer_modifier_logic.handle_input_changed(args)

def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
   resizer_modifier_logic.handle_validate_input(args)

def command_pre_select_start(args: adsk.core.SelectionEventHandler):
    resizer_modifier_logic.handle_pre_select_start(args)

def command_pre_select_stop(args: adsk.core.SelectionEventHandler):
    resizer_modifier_logic.handle_pre_select_stop(args)

def command_destroy(args: adsk.core.CommandEventArgs):
    
    
    global local_handlers
    local_handlers = []
