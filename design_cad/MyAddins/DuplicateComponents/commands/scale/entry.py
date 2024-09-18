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

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_scale_components'
CMD_NAME = 'Scale'
CMD_Description = 'Scales bodies. <br> <br> Select the objects to scale, then specify the scale factor.'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')
ICON_UNIFORM_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/uniform', '')
ICON_NONUNIFORM_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/nonuniform', '')

local_handlers = []
createdPoints = []
isPointSelected: bool = False

# TOOLTIPS
selection_input_tooltip = 'Select bodies to scale.'
point_input_tooltip = 'Select a point serving as the center of the scale operation.'
scaleType_tooltip = 'Select the type of scaling to perform.'
scale_tooltip = 'Enter the scale factor.'
scaleX_tooltip = 'Enter the scale factor for the X axis.'
scaleY_tooltip = 'Enter the scale factor for the Y axis.'
scaleZ_tooltip = 'Enter the scale factor for the Z axis.'

# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    initWorkspace(ui, WORKSPACE_MANUFACTURE, PANEL_MANUFACTURE, ARRANGE_STRATEGY, cmd_def, False)

# Executed when add-in is stopped.
def stop():
    cleanup(ui, WORKSPACE_MANUFACTURE,PANEL_MANUFACTURE, ARRANGE_STRATEGY, CMD_ID, False)

def command_created(args: adsk.core.CommandCreatedEventArgs):
    inputs = args.command.commandInputs

    args.command.setDialogInitialSize(400,300)

    # Create a selection input.
    selectionInput = inputs.addSelectionInput('selection', 'Entities', 'Select a body or mesh to scale')
    selectionInput.setSelectionLimits(1, 0)
    selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.Bodies)
    selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.MeshBodies)
    selectionInput.clearSelection()
    selectionInput.tooltip = selection_input_tooltip
    
    # Create a selection input.
    pointInput = inputs.addSelectionInput('point', 'Point', 'Select a point')
    pointInput.setSelectionLimits(1, 1)
    pointInput.addSelectionFilter(adsk.core.SelectionCommandInput.Vertices)
    pointInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchPoints)
    pointInput.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPoints)
    pointInput.clearSelection()
    pointInput.tooltip = point_input_tooltip

    # Create dropdown input that lists materials.
    scaleTypeDropdown = inputs.addDropDownCommandInput('scaleOption', 'Scale Type', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
    scaleTypeDropdown.tooltip = scaleType_tooltip
    #Add the options for the dropdown menu
    options = scaleTypeDropdown.listItems
    options.add('Uniform', True, ICON_UNIFORM_FOLDER)
    options.add('Non Uniform', False, ICON_NONUNIFORM_FOLDER)

    initial_value = adsk.core.ValueInput.createByReal(1)
    factor_val = inputs.addValueInput('factor', 'Scale Factor', '', initial_value)
    factor_val.isVisible = True
    factor_val.minimumValue = 0.0001
    factor_val.tooltip = scale_tooltip

    factorX_val = inputs.addValueInput('factorX', 'X Scale', '', initial_value)
    factorX_val.isVisible = False
    factorX_val.minimumValue = 0.0001
    factorX_val.tooltip = scaleX_tooltip

    factorY_val = inputs.addValueInput('factorY', 'Y Scale', '', initial_value)
    factorY_val.isVisible = False
    factorY_val.minimumValue = 0.0001
    factorY_val.tooltip = scaleY_tooltip

    factorZ_val = inputs.addValueInput('factorZ', 'Z Scale', '', initial_value)
    factorZ_val.isVisible = False
    factorZ_val.minimumValue = 0.0001
    factorZ_val.tooltip = scaleZ_tooltip

    # Add handlers for preview and destroy
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

def command_input_changed(args: adsk.core.InputChangedEventArgs):

    global isPointSelected
    global createdPoints

    inputs = args.inputs
    scale_options: adsk.core.DropDownCommandInput = inputs.itemById('scaleOption')
    point_selection: adsk.core.SelectionCommandInput = inputs.itemById('point')
    component_selection: adsk.core.SelectionCommandInput = inputs.itemById('selection')

    activeInput = args.input
    if (activeInput == scale_options):
        factor: adsk.core.ValueCommandInput = inputs.itemById('factor')
        factorX: adsk.core.ValueCommandInput = inputs.itemById('factorX')
        factorY: adsk.core.ValueCommandInput = inputs.itemById('factorY')
        factorZ: adsk.core.ValueCommandInput = inputs.itemById('factorZ')

        if scale_options.selectedItem.name == 'Uniform':
            factor.isVisible = True
        else:
            factor.isVisible = False
        factorX.isVisible = not factor.isVisible
        factorY.isVisible = not factor.isVisible
        factorZ.isVisible = not factor.isVisible
    elif(activeInput == component_selection and not isPointSelected):
        point_selection.clearSelection()
        if (component_selection.selectionCount == 0):
            return
        selectedBody = component_selection.selection(0).entity
        (selectedOccurrence, selectedComponent, parent_component, design) = getFilteredSelection(selectedBody.assemblyContext)

        if parent_component == None:
            ui.messageBox("Must select a component from a manufacturing model.")
            component_selection.clearSelection()
            return
        constructionPoints = parent_component.constructionPoints
        oldPoint = constructionPoints.itemByName('Scale Center')
        if(oldPoint != None):
            oldPoint.deleteMe()

        baseBody = selectedBody.nativeObject
        selectedBody = baseBody.createForAssemblyContext(selectedOccurrence)
        tempSourceComponent = selectedOccurrence.sourceComponent
        constructionPoint = selectedOccurrence.component.originConstructionPoint.createForAssemblyContext(selectedOccurrence)
        constructionPoint.name = 'Scale Center'
        point_selection.addSelection(constructionPoint)
    elif(activeInput == point_selection):
        isPointSelected = point_selection.selectionCount > 0

def command_preview(args: adsk.core.CommandEventArgs):
    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs

    # Getting our inputs here
    selectionInput: adsk.core.SelectionCommandInput = inputs.itemById('selection')
    pointInput: adsk.core.SelectionCommandInput = inputs.itemById('point')
    factor: adsk.core.ValueCommandInput = inputs.itemById('factor')
    factorX: adsk.core.ValueCommandInput = inputs.itemById('factorX')
    factorY: adsk.core.ValueCommandInput = inputs.itemById('factorY')
    factorZ: adsk.core.ValueCommandInput = inputs.itemById('factorZ')

    factorValueX = factorX.value
    factorValueY = factorY.value
    factorValueZ = factorZ.value
    if factor.isVisible:
        if not factor.isValidExpression:
            return
        factorValueX = factor.value
        factorValueY = factor.value
        factorValueZ = factor.value
    else:
        if not factorX.isValidExpression or not factorY.isValidExpression or not factorZ.isValidExpression:
            return

    if selectionInput.selectionCount == 0:
        return
    selectedBody: adsk.fusion.BrepBody = selectionInput.selection(0).entity
    (selectedOccurrence, selectedComponent, parent_component, design) = getFilteredSelection(selectedBody.assemblyContext)
    
    products = app.activeDocument.products
    baseDesign = products.item(0) # the very first one is always the idealization model from design
    activeProduct = app.activeProduct
    product = products.itemByProductType('CAMProductType')
    
    # in design or the MM we don't need the check, but in manufacturing we need to check whether the design we work with is a MM,
    # otherwise we'll change the design asset while in manufacture.
    if baseDesign == design and activeProduct == product :
        ui.messageBox("Must select a component from a manufacturing model.")
        selectionInput.clearSelection()
        return

    selectedPointBase = pointInput.selection(0).entity
    pointOccurrence = selectedPointBase.assemblyContext
    (pointOccurrence, dummy_selectedComponent, dummy_parent_component, dummy_design) = getFilteredSelection(pointOccurrence)
    nativePoint = selectedPointBase.nativeObject
    selectedPointBase = nativePoint.createForAssemblyContext(pointOccurrence)

    if design.designType == 1:
        is_parametric = True
        timelines = design.timeline
    else:
        is_parametric = False

    selectedOccurrences = adsk.core.ObjectCollection.create()
    i = 0
    baseBody = selectedBody.nativeObject
    selectedBody = baseBody.createForAssemblyContext(selectedOccurrence)

    selectedOccurrences.add(selectedBody)

    scales = parent_component.features.scaleFeatures
    scaleFactor = adsk.core.ValueInput.createByReal(factorValueX)
    scaleInput = scales.createInput(selectedOccurrences, selectedPointBase, scaleFactor)
        
    if factorX.isVisible:
        # Set the scale to be non-uniform
        xScale = adsk.core.ValueInput.createByReal(factorValueX)
        yScale = adsk.core.ValueInput.createByReal(factorValueY)
        zScale = adsk.core.ValueInput.createByReal(factorValueZ)
        scaleInput.setToNonUniform(xScale, yScale, zScale)
        
    scale = scales.add(scaleInput)
        
    if is_parametric:
        end_pos = timelines.markerPosition

    args.isValidResult = True

def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers

    if (args.terminationReason == adsk.core.CommandTerminationReason.CompletedTerminationReason):
        products = app.activeDocument.products
        camProduct = None
        try:
            # Mess up in the documentation, an exception is thrown if the product type is not found instead of returning null!
            camProduct: adsk.cam.CAM = products.itemByProductType('CAMProductType')
            # Ensure we invalidate operations affected by the scale feature.
            camProduct.checkValidity()
        except:
            camProduct = None

    local_handlers = []
