import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
from .circle_mah import *
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_circleMidAirHole'
CMD_NAME = 'Circle mid air hole'
CMD_Description = 'Circle mid air hole for supportless 3d printing.'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
COMMAND_BESIDE_ID = 'GEAR_3dpModelingTool'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Value template setting
template_list = {'Custom':(3.5,6.5,2.5), 'M2':(2.5,4.5,2.5), 'M2.5':(3,5.5,2.5), 'M3':(3.5,6.5,2.5), 'M4':(4.5,8,3), 'M5':(5.5,9.5,3.5), 'M6':(6.5,11,4)}

# Executed when add-in is run.
def start():
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

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # select component
    sel_body = inputs.addSelectionInput('body_select', 'Body', 'Select body')
    sel_body.selectionFilters = ['Bodies']
    sel_body.setSelectionLimits(1, 1)
    # select point    
    sel_point = inputs.addSelectionInput('point_select', 'Point', 'Select point')
    sel_point.selectionFilters = ['SketchPoints', 'SketchCircles', 'CircularEdges']
    sel_point.setSelectionLimits(1, 0)
    # value input
    template = inputs.addDropDownCommandInput('template', 'Value template', adsk.core.DropDownStyles.TextListDropDownStyle)
    list_items = template.listItems
    flag = True
    for key in template_list.keys():
        list_items.add(key, flag, '')
        if flag:
            flag = False
    inputs.addValueInput('layer_thick', 'Layer thickness', 'mm',  adsk.core.ValueInput.createByReal(0.02))
    inputs.addValueInput('large_hole', 'Large hole diamter', 'mm',  adsk.core.ValueInput.createByReal(0.2))
    inputs.addValueInput('large_depth', 'Large hole depth', 'mm',  adsk.core.ValueInput.createByReal(0.1))
    inputs.addValueInput('small_hole', 'Small hole diamter', 'mm',  adsk.core.ValueInput.createByReal(0.1))
    inputs.addValueInput('small_depth', 'Small hole depth', 'mm',  adsk.core.ValueInput.createByReal(1.0))

    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    sel_body: adsk.core.SelectionCommandInput = inputs.itemById('body_select')
    sel_point: adsk.core.SelectionCommandInput = inputs.itemById('point_select')
    layer_thick: adsk.core.ValueCommandInput = inputs.itemById('layer_thick')
    large_hole: adsk.core.ValueCommandInput = inputs.itemById('large_hole')
    large_depth: adsk.core.ValueCommandInput = inputs.itemById('large_depth')
    small_hole: adsk.core.ValueCommandInput = inputs.itemById('small_hole')
    small_depth: adsk.core.ValueCommandInput = inputs.itemById('small_depth')


    # preparation
    target_body = adsk.fusion.BRepBody.cast(sel_body.selection(0).entity)
    comp = target_body.parentComponent

    futil.log('len:{0}'.format(sel_point.selectionCount))
    ents = [sel_point.selection(i).entity for i in range(sel_point.selectionCount)]
    futil.log('len:{0}'.format(len(ents)))

    tool_body = create_circle_mah_tool(comp, layer_thick.value, large_hole.value, large_depth.value, small_hole.value, small_depth.value)
    for ent in ents:
        futil.log('type:{0}'.format(ent))
        if type(ent) is adsk.fusion.SketchPoint:
            futil.log('target is SketchPoint')
            point = adsk.fusion.SketchPoint.cast(ent)
            cut_circle_mah_by_point(target_body, tool_body, point)
        elif type(ent) is adsk.fusion.SketchCircle:
            futil.log('target is SketchCircle')
            circle = adsk.fusion.SketchCircle.cast(ent)
            cut_circle_mah_by_point(target_body, tool_body, circle.centerSketchPoint)
        elif type(ent) is adsk.fusion.BRepEdge:
            edge = adsk.fusion.BRepEdge.cast(ent)
            if (isinstance(edge.geometry, adsk.core.Circle3D)):
                futil.log('target is Circle3D')
                cut_circle_mah_by_3dcircle(target_body, tool_body, edge.geometry)
    # not visible
    tool_body.isVisible = False



# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    #futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs
    


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    # template
    template: adsk.core.DropDownCommandInput() = inputs.itemById('template')
    item = template.selectedItem
    arr = template_list[item.name]
    # value
    large_hole: adsk.core.ValueCommandInput = inputs.itemById('large_hole')
    large_depth: adsk.core.ValueCommandInput = inputs.itemById('large_depth')
    small_hole: adsk.core.ValueCommandInput = inputs.itemById('small_hole')
    large_hole.value = arr[1] / 10.0
    large_depth.value = arr[2] / 10.0
    small_hole.value = arr[0] / 10.0

    # General logging for debug.
    #futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    #futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    enflag = True
    # inputs
    sel_body: adsk.core.SelectionCommandInput = inputs.itemById('body_select')
    sel_point: adsk.core.SelectionCommandInput = inputs.itemById('point_select')
    layer_thick: adsk.core.ValueCommandInput = inputs.itemById('layer_thick')
    large_hole: adsk.core.ValueCommandInput = inputs.itemById('large_hole')
    large_depth: adsk.core.ValueCommandInput = inputs.itemById('large_depth')
    small_hole: adsk.core.ValueCommandInput = inputs.itemById('small_hole')
    small_depth: adsk.core.ValueCommandInput = inputs.itemById('small_depth')
    # check
    if sel_body.selectionCount == 0:
        enflag = False
    if sel_point.selectionCount == 0:
        enflag = False
    if layer_thick.value < 0:
        enflag = False
    if large_hole.value <= 0:
        enflag = False
    if large_depth.value < 0:
        enflag = False
    if small_hole.value <= 0:
        enflag = False
    if small_depth.value < 0:
        enflag = False
    # enable
    args.areInputsValid = enflag

        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
