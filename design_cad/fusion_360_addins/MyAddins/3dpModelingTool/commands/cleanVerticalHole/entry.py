import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
from .cvh import *
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cleanVerticalHole'
CMD_NAME = 'Clean vertical hole'
CMD_Description = 'Clean vertical hole for correct vertical length.'

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
    sel_face = inputs.addSelectionInput('face_select', 'Bottom face', 'Select face')
    sel_face.selectionFilters = ['PlanarFaces']
    sel_face.setSelectionLimits(1, 1)
    # select point    
    sel_point = inputs.addSelectionInput('point_select', 'Point', 'Select point')
    sel_point.selectionFilters = ['SketchPoints', 'SketchCircles', 'CircularEdges']
    sel_point.setSelectionLimits(1, 0)
    # calcurate patern
    #patern = inputs.addDropDownCommandInput('patern', 'Calculate pattern', adsk.core.DropDownStyles.TextListDropDownStyle)
    #list_items = patern.listItems
    #list_items.add('angle&thick', True, '')
    # value input
    inputs.addValueInput('layer_thick', 'Layer thickness', 'mm',  adsk.core.ValueInput.createByReal(0.02))
    inputs.addValueInput('hole', 'Hole diameter', 'mm',  adsk.core.ValueInput.createByReal(0.3))
    inputs.addValueInput('angle', 'Tangent angle', 'degree',  adsk.core.ValueInput.createByReal(math.radians(30.0)))
    inputs.addValueInput('width', 'Top width', 'mm',  adsk.core.ValueInput.createByReal(0.1))
    inputs.addValueInput('depth', 'Hole depth', 'mm',  adsk.core.ValueInput.createByReal(1.0))

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
    sel_face: adsk.core.SelectionCommandInput = inputs.itemById('face_select')
    sel_point: adsk.core.SelectionCommandInput = inputs.itemById('point_select')
    layer_thick: adsk.core.ValueCommandInput = inputs.itemById('layer_thick')
    hole: adsk.core.ValueCommandInput = inputs.itemById('hole')
    angle: adsk.core.ValueCommandInput = inputs.itemById('angle')
    width: adsk.core.ValueCommandInput = inputs.itemById('width')
    depth: adsk.core.ValueCommandInput = inputs.itemById('depth')


    # preparation
    target_face = adsk.fusion.BRepFace.cast(sel_face.selection(0).entity)
    comp = target_face.body.parentComponent
    
    ents = [sel_point.selection(i).entity for i in range(sel_point.selectionCount)]

    #(b_norm, b_fa, b_fb, b_fc, b_fd) = get_face_formula(target_face)
    b_norm = get_face_formula(target_face)
    #tool_body = create_cvh_tool_by_ah(comp, hole.value, depth.value, angle.value, layer_thick.value)

    #futil.log('norm:{0},fa:{1},fb:{2},fc:{3},fd:{4}'.format(b_norm, b_fa, b_fb, b_fc, b_fd))
    for ent in ents:
        if type(ent) is adsk.fusion.SketchPoint:
            futil.log('target is SketchPoint')
            point = adsk.fusion.SketchPoint.cast(ent)
            vector = get_vector_by_point(b_norm, point)
            (sketch, rotth, startIndex) = get_sketch_by_point(target_face, vector, point)
            cut_cvh_tool_by_ah(comp, sketch, rotth, startIndex, hole.value, depth.value, angle.value, layer_thick.value)
        elif type(ent) is adsk.fusion.SketchCircle:
            futil.log('target is SketchCircle')
            circle = adsk.fusion.SketchCircle.cast(ent)
            vector = get_vector_by_point(b_norm, circle.centerSketchPoint)
            (sketch, rotth, startIndex) = get_sketch_by_point(target_face, vector, circle.centerSketchPoint)
            cut_cvh_tool_by_ah(comp, sketch, rotth, startIndex, hole.value, depth.value, angle.value, layer_thick.value)
        elif type(ent) is adsk.fusion.BRepEdge:
            edge = adsk.fusion.BRepEdge.cast(ent)
            if (isinstance(edge.geometry, adsk.core.Circle3D)):
                futil.log('target is Circle3D')
                vector = get_vector_by_3dcircle(b_norm, edge.geometry)
                (sketch, rotth, startIndex) = get_sketch_by_3dcircle(target_face, vector, edge.geometry)
                cut_cvh_tool_by_ah(comp, sketch, rotth, startIndex, hole.value, depth.value, angle.value, layer_thick.value)

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
    sel_face: adsk.core.SelectionCommandInput = inputs.itemById('face_select')
    sel_point: adsk.core.SelectionCommandInput = inputs.itemById('point_select')
    layer_thick: adsk.core.ValueCommandInput = inputs.itemById('layer_thick')
    hole: adsk.core.ValueCommandInput = inputs.itemById('hole')
    angle: adsk.core.ValueCommandInput = inputs.itemById('angle')
    width: adsk.core.ValueCommandInput = inputs.itemById('width')
    depth: adsk.core.ValueCommandInput = inputs.itemById('depth')
    # check
    if sel_face.selectionCount == 0:
        enflag = False
    if sel_point.selectionCount == 0:
        enflag = False
    if layer_thick.value < 0:
        enflag = False
    if hole.value <= 0:
        enflag = False
    if angle.value < 0:
        enflag = False
    if width.value < 0:
        enflag = False
    if depth.value < 0:
        enflag = False
    # enable
    args.areInputsValid = enflag        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
