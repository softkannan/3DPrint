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
import adsk.cam
import os

IS_PROMOTED = False

app = adsk.core.Application.get()

# Working in DESIGN
WORKSPACE_DESIGN = 'FusionSolidEnvironment'
WORKSPACE_MANUFACTURINGMODEL = 'MfgWorkingModelEnv'
WORKSPACE_MANUFACTURE = 'CAMEnvironment'
PANEL_DESIGN = 'SolidCreatePanel'
PANEL_MANUFACTURE = 'CAMAdditivePositioningPanel'
DROPDOWN = 'PatternDropDown'
ARRANGE_STRATEGY = 'IronStrategy_additive_arrange_strategy'

COMMAND_BESIDE_DESIGN = 'PatternDropDown'
COMMAND_BESIDE_MANUFACTURE = 'PatternDropDown'

def initWorkspace(ui, workspaceid, panelid, dropdownid, cmd_def, hasdropdown):
    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace1 = ui.workspaces.itemById(workspaceid)

    # Get the panel the button will be created in.
    panel1 = workspace1.toolbarPanels.itemById(panelid)

    if hasdropdown:
        # get the dropdown the button will be created in
        dropdown = panel1.controls.itemById(dropdownid)

        # Create the button command control in the UI after the specified existing command.
        control1 = dropdown.controls.addCommand(cmd_def)
    else:
        control1 = panel1.controls.addCommand(cmd_def)

    # Specify if the command is promoted to the main toolbar. 
    control1.isPromoted = IS_PROMOTED


def cleanup(ui, workspaceid,panelid, dropdownid,commandid, hasdropdown):
# Get the various UI elements for this command
    workspace = ui.workspaces.itemById(workspaceid)
    panel = workspace.toolbarPanels.itemById(panelid)
    if hasdropdown:
        dropdown = panel.controls.itemById(dropdownid)
        command_control = dropdown.controls.itemById(commandid)
    else:
        command_control = panel.controls.itemById(commandid)
    command_definition = ui.commandDefinitions.itemById(commandid)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()

def getFilteredSelection(occ : adsk.fusion.Occurrence):
    selectedComponent: adsk.fusion.Component = occ.component
    design = selectedComponent.parentDesign
    if (design == None):
        # for some reason, we don't have a design, return null for all
        return None, None, None, None


    products = app.activeDocument.products
    designProduct = products.item(0) # the very first one is always the idealization model from design
    activeProduct = app.activeProduct
    camProduct = None
    try:
        # mess up in the documentation, an exception is thrown if the product type is not found instead of returning null!
        camProduct: adsk.cam.CAM = products.itemByProductType('CAMProductType')
    except:
        camProduct = None

    usedManufacturingModelRootOcc = None
    if (activeProduct == designProduct):
        if (design == designProduct):
            # nothing to do here, we already deal with the design path in the design workspace
            return occ, selectedComponent, occ.sourceComponent, design
        else:
            # we ended up with a manufacturing model inside the design workspace
            # this should never happen, return null for all
            return None, None, None, None
    elif (camProduct != None and activeProduct == camProduct):
        # we're inside Manufacture, thus we should only allow manufacturing models
        if (design == designProduct):
            # return null, we're dealing with the idealization model
            return None, None, None, None
        '''else:
            # get the manufacturing model from CAM
            manufacturingModels = camProduct.manufacturingModels
            for manufacturingModel in manufacturingModels:
                if manufacturingModel.occurrence.component.parentDesign == design:
                    usedManufacturingModelRootOcc = manufacturingModel.occurrence
                    break
                test = manufacturingModel.occurrence.sourceComponent
                if test == None:
                    continue'''
    elif adsk.fusion.Design.cast(activeProduct) != None:
        # we're inside the manufacturing model edit workspace, treat it the same as the design workspace
        return occ, selectedComponent, occ.sourceComponent, design
    else:
        # we're in some other product, return null
        return None, None, None, None


    # design.rootComponent would give us the i.e. manufacturing model itself.
    # not usable if we want to place the copy into the same parent component. 
    occs = []
    nextOcc = occ
    while nextOcc and (nextOcc.component != design.rootComponent):
        occs.insert(0, nextOcc)
        nextOcc = nextOcc.assemblyContext
    #occs should now be a list starting at the top most occurrence and ending at the "selected" occurrence
    
    childOccurrences: adsk.fusion.OccurrenceList = design.rootComponent.occurrences
    parent_component = design.rootComponent
    for i in range(len(occs)):
        children = childOccurrences
        for j in range(len(children)):
            if children.item(j).name == occs[i].name:
                #if (i > 0):
                #    parent_component = usedManufacturingModelRootOcc.component  
                usedManufacturingModelRootOcc = children.item(j)
                childOccurrences = usedManufacturingModelRootOcc.childOccurrences
                break
    
    if not parent_component:
        return None, None, None, None

    fixedOccurrence = usedManufacturingModelRootOcc
    selectedComponent = fixedOccurrence.component
    return fixedOccurrence, selectedComponent, parent_component, design

def getActiveSetup(app: adsk.core.Application):
    products = app.activeDocument.products
    activeProduct = app.activeProduct
    camProduct = None
    try:
        # mess up in the documentation, an exception is thrown if the product type is not found instead of returning null!
        camProduct: adsk.cam.CAM = products.itemByProductType('CAMProductType')
    except:
        return None
    if camProduct != activeProduct: 
        return None
    # get the active setup
    for i in range (camProduct.setups.count):
        if camProduct.setups.item(i).isActive:
            return camProduct.setups.item(i)

# returns the CAM product, bu tonly if we're in the CAM workspace
def getCAMProduct(app: adsk.core.Application):
    products = app.activeDocument.products
    activeProduct = app.activeProduct
    camProduct = None
    try:
        # mess up in the documentation, an exception is thrown if the product type is not found instead of returning null!
        camProduct: adsk.cam.CAM = products.itemByProductType('CAMProductType')
    except:
        return None
    if camProduct != activeProduct:
        return None
    return camProduct
