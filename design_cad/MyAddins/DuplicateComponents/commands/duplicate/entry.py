#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.
import adsk.core
import adsk.fusion
import os
from ...lib import fusion360utils as futil
from ... import config
from ..cmdHelper import *

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_duplicate_components'
CMD_NAME = 'Duplicate Components'
CMD_Description = 'Duplicates components in the active workspace either in place or distributes them in rows to create a pattern along a specific axis. <br> <br> Select the component to pattern in the canvas or browser. Specify the number of duplicate components that should be created. Select how the duplicated components should be arranged. Choose whether you want the duplicate components to be instances or independent components.'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

local_handlers = []
isFirstSelectionInitialization = True
newOccurrences = []

# TOOLTIPS
selection_input_tooltip = 'Select a component to duplicate.'
num_copies_tooltip = 'Specify the number of duplicate components that should be created.'
arrange_tooltip = 'Select how the duplicated components should be arranged.'
spacing_tooltip ='Distance between the bounding box of the duplicated components.'
pasteNew_tooltip = 'Paste New creates a new copy of your component.'
pasteNew_tooltip_description = 'By default, this command creates instances of the selected component. The Paste New option creates new components that are not instances of the original component.'
addToSetupBool_tooltip = 'Add the new components to the active setup.'
addToSetupBool_tooltip_description = 'By default, this command adds new components to the active setup.'

# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    initWorkspace(ui, WORKSPACE_DESIGN, PANEL_DESIGN, DROPDOWN, cmd_def, True)
    initWorkspace(ui, WORKSPACE_MANUFACTURINGMODEL, PANEL_DESIGN, DROPDOWN, cmd_def, True)
    initWorkspace(ui, WORKSPACE_MANUFACTURE, PANEL_MANUFACTURE, ARRANGE_STRATEGY, cmd_def, False)

# Executed when add-in is stopped.
def stop():
    cleanup(ui, WORKSPACE_DESIGN, PANEL_DESIGN, DROPDOWN, CMD_ID, True)
    cleanup(ui, WORKSPACE_MANUFACTURINGMODEL,PANEL_DESIGN, DROPDOWN, CMD_ID, True)
    cleanup(ui, WORKSPACE_MANUFACTURE,PANEL_MANUFACTURE, ARRANGE_STRATEGY, CMD_ID, False)

def command_created(args: adsk.core.CommandCreatedEventArgs):
    global isFirstSelectionInitialization
    isFirstSelectionInitialization = True

    inputs = args.command.commandInputs

    args.command.setDialogInitialSize(400,300)

    # Create a selection input.
    selectionInput = inputs.addSelectionInput('selection', 'Select', 'Select a component to duplicate')
    selectionInput.setSelectionLimits(1, 1)
    selectionInput.addSelectionFilter("Occurrences")
    selectionInput.clearSelection()
    selectionInput.tooltip = selection_input_tooltip

    # Create integer  input.
    int_input = inputs.addIntegerSpinnerCommandInput('spinnerInt', 'Number of Copies', 1, 1000, 1, 1)
    int_input.tooltip = num_copies_tooltip

    # Create dropdown input that lists materials.
    arrange_dropdown = inputs.addDropDownCommandInput('arrangeOption', 'Arrange', adsk.core.DropDownStyles.TextListDropDownStyle)
    arrange_dropdown.tooltip = arrange_tooltip
    #Add the options for the dropdown menu
    options = arrange_dropdown.listItems
    options.add('Same Location', True, '')
    options.add('Arrange in X', False, '')
    options.add('Arrange in Y', False, '')
    options.add('Arrange in Z', False, '')

    initial_value = adsk.core.ValueInput.createByReal(1)
    spacing_val = inputs.addValueInput('spacing', 'Spacing', 'mm', initial_value)
    spacing_val.isVisible = False
    spacing_val.tooltip = spacing_tooltip

    bool_input = inputs.addBoolValueInput('paste_new', 'Copy & Paste New method', True)
    bool_input.tooltip = pasteNew_tooltip
    bool_input.tooltipDescription = pasteNew_tooltip_description
    bool_input.isVisible = getCAMProduct(app) == None

    addToSetupBool_input = inputs.addBoolValueInput('add_to_setup', 'Add to active setup', True)
    addToSetupBool_input.tooltip = addToSetupBool_tooltip
    addToSetupBool_input.tooltipDescription = addToSetupBool_tooltip_description
    addToSetupBool_input.isVisible = getActiveSetup(app) != None

    # Add handlers for preview and destroy
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    global isFirstSelectionInitialization
    global newOccurrences

    changed_input = args.input
    inputs = args.inputs
    arrange_selected: adsk.core.DropDownCommandInput = inputs.itemById('arrangeOption')
    spacing: adsk.core.ValueCommandInput = inputs.itemById('spacing')
    selectionInput : adsk.core.SelectionCommandInput = inputs.itemById('selection')

    if arrange_selected.selectedItem.name == 'Same Location':
        spacing.isVisible = False
    else:
        spacing.isVisible = True

    if (changed_input == selectionInput and isFirstSelectionInitialization):
        isFirstSelectionInitialization = False
        selectionInput.clearSelection()

def command_preview(args: adsk.core.CommandEventArgs):
    global newOccurrences
    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs 

    # Getting our inputs here
    selectionInput: adsk.core.SelectionCommandInput = inputs.itemById('selection')
    spinnerInput: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('spinnerInt')
    arrange_selected: adsk.core.DropDownCommandInput = inputs.itemById('arrangeOption')
    spacing: adsk.core.ValueCommandInput = inputs.itemById('spacing')
    paste_new: adsk.core.BoolValueCommandInput = inputs.itemById('paste_new')
    addToSetup: adsk.core.BoolValueCommandInput = inputs.itemById('add_to_setup')

    selectedOccurrence: adsk.fusion.Occurrence = selectionInput.selection(0).entity
    if selectedOccurrence.objectType != adsk.fusion.Occurrence.classType():
        ui.messageBox("Can't select root component.")
        selectionInput.clearSelection()
        return
    
    (selectedOccurrence, selectedComponent, parent_component, design) = getFilteredSelection(selectedOccurrence)

    if selectedOccurrence == None:
        ui.messageBox("Input must be part of a manufacturing model.")
        selectionInput.clearSelection()
        return
    
    if design.designType == 1:
        is_parametric = True
        snapshots=design.snapshots
        timelines = design.timeline
        start_pos = timelines.markerPosition
    else:
        is_parametric = False

    numberComponents = spinnerInput.value

    bounding_box = selectedOccurrence.boundingBox

    # Used to setup x transformation
    max_point_x = bounding_box.maxPoint.x
    bounding_box_x = max_point_x - bounding_box.minPoint.x
    x_increment = bounding_box_x + spacing.value

    # Used to setup y transformation
    max_point_y = bounding_box.maxPoint.y
    bounding_box_y = max_point_y - bounding_box.minPoint.y
    y_increment = bounding_box_y + spacing.value

    # Used to setup z transformation
    max_point_z = bounding_box.maxPoint.z
    bounding_box_z = max_point_z - bounding_box.minPoint.z
    z_increment = bounding_box_z + spacing.value

    newOccurrences = []
    for i in range(numberComponents):
        # Create a transform for the copied component
        transformMatrix = selectedOccurrence.transform

        # Increment copies of component in x direction
        if arrange_selected.selectedItem.name == 'Arrange in X':
            x_transform = ((i + 1) * x_increment)
            x_vector = adsk.core.Vector3D.create(1, 0, 0)
            x_vector.scaleBy(x_transform)
            x_vector.add(transformMatrix.translation)
            transformMatrix.translation = x_vector
        elif arrange_selected.selectedItem.name == 'Arrange in Y':
            y_transform = ((i + 1) * y_increment)
            y_vector = adsk.core.Vector3D.create(0, 1, 0)
            y_vector.scaleBy(y_transform)
            y_vector.add(transformMatrix.translation)
            transformMatrix.translation = y_vector
        elif arrange_selected.selectedItem.name == 'Arrange in Z':
            z_transform = ((i + 1) * z_increment)
            z_vector = adsk.core.Vector3D.create(0, 0, 1)
            z_vector.scaleBy(z_transform)
            z_vector.add(transformMatrix.translation)
            transformMatrix.translation = z_vector

        # Create a copy of the original component
        if paste_new.value == True:
            newOccurrences.append(parent_component.occurrences.addNewComponentCopy(selectedComponent, transformMatrix))
        elif paste_new.value == False:
            newOccurrences.append(parent_component.occurrences.addExistingComponent(selectedComponent, transformMatrix))
        
        #Creates the Capture position / snapshot feature if necessary
        if is_parametric:
            if snapshots.hasPendingSnapshot:
                snapshots.add()

    if is_parametric:
        end_pos = timelines.markerPosition

        # Only create a timeline group if more that one copy is created
        if numberComponents > 1:
            timelines.timelineGroups.add(start_pos, end_pos - 1)
    args.isValidResult = True

def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    global newOccurrences
    global app

    if (args.terminationReason == adsk.core.CommandTerminationReason.CompletedTerminationReason):
        camProduct = getCAMProduct(app)

        if camProduct != None:
            # get the active setup
            activeSetup = getActiveSetup(app)

            addToSetup: adsk.core.DropDownCommandInput = args.command.commandInputs.itemById('add_to_setup')
            if activeSetup != None and addToSetup.value == True:
                objectCol = activeSetup.models
                for occurrence in newOccurrences:
                    objectCol.add(occurrence)
                activeSetup.models = objectCol
            camProduct.checkValidity()

    local_handlers = []
    newOccurrences = []
