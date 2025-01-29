#Author-Eirinn
#Description-Generates a lid to cap an open face

import adsk.core, adsk.fusion, adsk.cam, traceback

# global set of event handlers to keep them referenced for the duration of the command
handlers = []

def messageBox(text):
    app = adsk.core.Application.get()
    ui  = app.userInterface
    ui.messageBox(str(text))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        lidButton = cmdDefs.addButtonDefinition('LidMakerButtonID', 'Lid', 'Creates a friction-fit lid on an open face.',
                                                './/resources')
        lidButton.toolClipFilename = './/resources/toolclip-256.png'
        # Connect to the command created event.
        commandCreated = CommandCreatedEventHandler()
        lidButton.commandCreated.add(commandCreated)
        handlers.append(commandCreated)
        
        # Get the CREATE panel in the model workspace. 
        CreatePanel = ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom.
        buttonControl = CreatePanel.controls.addCommand(lidButton, 'FusionHoleCommand')

        # Make the button available in the panel.
        buttonControl.isPromotedByDefault = True
        buttonControl.isPromoted = True
        # Execute the command.
        # lidButton.execute()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('LidMakerButtonID')
        if cmdDef:
            cmdDef.deleteMe()  
        # Get panel the control is in.
        CreatePanel = ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Get and delete the button control.
        buttonControl = CreatePanel.controls.itemById('LidMakerButtonID')
        if buttonControl:
            buttonControl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the commandCreated event.
class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Get the command
            cmd = eventArgs.command

            # Get the CommandInputs collection to create new command inputs.            
            inputs = cmd.commandInputs

            des = adsk.fusion.Design.cast(app.activeProduct)

            selector = inputs.addSelectionInput('selection','Profile','Select a planar face with a hole')
            selector.addSelectionFilter('PlanarFaces')
            #connect to the selector event
            

            inputs.addValueInput('height', 'Height', 
                                            des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.2))                            
            thicknessSlider = inputs.addFloatSliderCommandInput('thickness', 'Thickness', 
                                            des.unitsManager.defaultLengthUnits, 
                                            0, 0.2, False)                            
            inputs.addValueInput('depth', 'Tab depth', 
                                            des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.25))
            inputs.addValueInput('width', 'Tab width', 
                                            des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.2))
            inputs.addValueInput('offset', 'Tab offset', 
                                            des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(0.02))
            thicknessSlider.valueOne = 0.2
            # Connect to the executePreview event.
            onExecutePreview = CommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            handlers.append(onExecutePreview)
            # and the selection event
            onSelect = SelectionEventHandler()
            cmd.selectionEvent.add(onSelect)
            handlers.append(onSelect)
            # and the input changed event
            onInputChanged = CommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

        except:
            if ui:
                ui.messageBox(traceback.format_exc())


class SelectionEventHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            eventArgs = adsk.core.SelectionEventArgs.cast(args)
            profile = eventArgs.selection.entity
            profile = adsk.fusion.BRepFace.cast(profile)
            if profile.loops.count == 2: #this is a face with a hole in it 
                eventArgs.isSelectable = True
            else:
                eventArgs.isSelectable = False

        except:
            ui.messageBox(traceback.format_exc())

        
class CommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            if changedInput.id == 'height':
                inputs = eventArgs.firingEvent.sender.commandInputs
                thicknessSlider = inputs.itemById('thickness')
                thicknessSlider.maximumValue = changedInput.value
                # set the thickness to the height. This might be annoying behaviour.
                thicknessSlider.valueOne = changedInput.value


        except:
            ui.messageBox(traceback.format_exc())


# Main Event. Handler for the executePreview event. 
class CommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            des = adsk.fusion.Design.cast(app.activeProduct)
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Get the values from the command inputs. 
            inputs = eventArgs.command.commandInputs
            #get the selected face
            
            selector = inputs.itemById('selection')
            offsetAmount = inputs.itemById('offset').value
            depth = inputs.itemById('depth').value
            height = inputs.itemById('height').value
            thickness = inputs.itemById('thickness').valueOne
            width = inputs.itemById('width').value
            
            face = selector.selection(0).entity
            face = adsk.fusion.BRepFace.cast(face)
            
            # make a new component
            # Create a new occurrence.	
            trans = adsk.core.Matrix3D.create()
            occ = des.rootComponent.occurrences.addNewComponent(trans)
            thisComp = occ.component
            startIndex = occ.timelineObject.index #this is for the timeline group

            newsketch = thisComp.sketches.add(face)
            # this sketch already has the face projected! 
            # but I want the inner loop
            innerLoop = face.loops[0]
            # innerLoop.
            loop_curves = adsk.core.ObjectCollection.create()
            for edge in innerLoop.edges:
                loop_curve_collection = newsketch.project(edge)
                for curve in loop_curve_collection:
                    loop_curves.add(curve)
            tabOuterCurves = newsketch.offset(loop_curves, face.centroid, offsetAmount)
            tabInnerCurves = newsketch.offset(loop_curves, face.centroid, offsetAmount+width)
            # now extrude. There should be 4 profiles 
            if len(newsketch.profiles) != 4:
                raise ValueError('Number of profiles is %s, expected 4' % len(newsketch.profiles))
            # iterate through these and put them in a collection. Check the sizes so we know which is the inner and which is the tab.
            perimeters = [] # use this list to hold the order of perimeters from large to small
            profiles_to_extrude = adsk.core.ObjectCollection.create()
            for idx, profile in enumerate(newsketch.profiles):
                profiles_to_extrude.add(profile)
                props = profile.areaProperties()
                perimeters.append((props.perimeter, profile))
            perimeters.sort()
            # now the innermost profile is the first one
            inside_lid_profile = perimeters[0][1]
            # the tab profile is the second smallest
            tab_profile = perimeters[1][1]
            # extrude all the profiles
            extrudes = thisComp.features.extrudeFeatures
            mainExtrude = extrudes.addSimple(profiles_to_extrude, adsk.core.ValueInput.createByReal(height), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            mainExtrude.name = 'LidHeight'
            newComp = mainExtrude.parentComponent
            newCompExtrudes = newComp.features.extrudeFeatures
            # that's the top done. Now extrude the tab.
            tabExtrude = newCompExtrudes.addSimple(tab_profile, adsk.core.ValueInput.createByReal(-depth), adsk.fusion.FeatureOperations.JoinFeatureOperation)
            tabExtrude.name = 'TabDepth'
            endIndex = tabExtrude.timelineObject.index
            # if thickness is less than height, we need to cut in with another extrude
            if thickness < height:
                lidCutExtrude = newCompExtrudes.addSimple(inside_lid_profile, adsk.core.ValueInput.createByReal(height-thickness), adsk.fusion.FeatureOperations.CutFeatureOperation)
                lidCutExtrude.name = 'LidCut'
                endIndex = lidCutExtrude.timelineObject.index
            newComp.name = 'Lid'

            # add these stesps to a timelinegroup
            # tgs = des.timeline.timelineGroups
            # tg = tgs.add(startIndex,endIndex)
            # tg.name = 'LidMaker'
            
            # Set the isValidResult property to use these results at the final result.
            # This will result in the execute event not being fired.
            eventArgs.isValidResult = True

        except:
            if ui:
                ui.messageBox(traceback.format_exc())
                