import adsk.core, adsk.fusion, adsk.cam, traceback, pdb
app = adsk.core.Application.get()
ui  = app.userInterface

#Default values
NozzleDiameter_Default = 0.4

#Other configurable values - values in cm!!!!!
WallThicnkessMin = 0.15
WallThicnkessMax = 0.5
WallThicnkessModifier = 0.1 #support wall 30mm height will be 30*modifier thick, 
SupportContainerName = "Support geometry"

#some developer options
RoundingPrecission = 3
OffsetPlaneZShift = -0.00
ChamferBottomPlane = True #if non XYbase plane is selected, bottom side of support geometry will be chamfered
AutomaticBasePlaneXY_Default = False
ChamferBottomPlane = True

def WallThicknessCalc(Height):  #output and input in cm
    Thickness = Height*WallThicnkessModifier
    if Thickness > WallThicnkessMax:
        return WallThicnkessMax
    elif Thickness < WallThicnkessMin:
        return WallThicnkessMin
    else:
        return Thickness

    

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        BSG_buttonSample = cmdDefs.addButtonDefinition('BridgeSupportGeometry_ID3', 
                                                   'Bridge support geometry', 
                                                   'Creates support geometry',
                                                   '') #didnt included icons
        
        # Connect to the command created event.
        BSG_CommandCreated = BSG_CommandCreatedEventHandler()
        BSG_buttonSample.commandCreated.add(BSG_CommandCreated)
        handlers.append(BSG_CommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(BSG_buttonSample)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class BSG_CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        
        # Get the command
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.            
        inputs = cmd.commandInputs

        des = adsk.fusion.Design.cast(app.activeProduct)
        if des.designType == 0:
            des.designType = adsk.fusion.DesignTypes.ParametricDesignType 
            ui.messageBox('Capture Design History turned on')

        
        SelectedLine = inputs.addSelectionInput('SelectedLine_ID','Line/Curve','Selected one or multiple Lines/Curves')
        SelectedLine.setSelectionLimits(1,0)
        SelectedLine.addSelectionFilter('SketchCurves')
        SelectedLine.addSelectionFilter('Edges')
        
        SelectedPlane = inputs.addSelectionInput('SelectedPlane_ID','Base Plane','Selected base plane. Default is origin XY')
        SelectedPlane.setSelectionLimits(1,1)
        SelectedPlane.addSelectionFilter('PlanarFaces')
        SelectedPlane.addSelectionFilter('Sketches')
        SelectedPlane.addSelectionFilter('ConstructionPlanes')
        
              
        
        SelectedPlane.addSelection(adsk.fusion.Design.cast(app.activeProduct).rootComponent.xYConstructionPlane)
        
        NozzleDiameter = inputs.addFloatSpinnerCommandInput('NozzleDiameter_ID', 'Nozzle Diameter',"mm", 0.0000001 , 2 , 0.1, NozzleDiameter_Default)

        onExecute = BSG_CommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)



# Event handler for the execute event. 
class BSG_CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)


        # Get the values from the command inputs. 
        inputs = eventArgs.command.commandInputs
        
        SelectedLine_Input = inputs.itemById('SelectedLine_ID')        
        SelectedPlane_Input = inputs.itemById('SelectedPlane_ID')
        NozzleDiameter_Input = inputs.itemById('NozzleDiameter_ID')
        
        global NozzleDiameter_Default
        
        NozzleDiameter_Default = NozzleDiameter_Input.value*10
        #try:

        CreateBridgeSupportGeometry(SelectedLine_Input,SelectedPlane_Input,NozzleDiameter_Input)
        #except:
        #    ui.messageBox("problem durring the geometry creation")


        

def CreateBridgeSupportGeometry(SelectedLine_Arg, SelectedPlane_Arg,NozzleDiameter_Arg):

    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    Sketches =  root.sketches
    RootOccs = root.occurrences
    transform = adsk.core.Matrix3D.create()
    OffsetPoint1 = adsk.core.Point3D.create(999.9,999.9,999.9)
    AutomaticBasePlaneXY = False
    ChamferBottomPlane = False

    Curve_sels= adsk.core.ObjectCollection.create()
    for x in range(0,SelectedLine_Arg.selectionCount):
        Curve_sels.add(SelectedLine_Arg.selection(x).entity)    
    SPlane = SelectedPlane_Arg.selection(0).entity
    #Find/create Support geometry component (container)
    SupportCompFound = False
    for x in range(0,RootOccs.count):
        if RootOccs.item(x).component.name == SupportContainerName:
            SupportContainer = RootOccs.item(x)
            SupportContainerComp = RootOccs.item(x).component
            SupportCompFound = True
            break
    if SupportCompFound == False:
        SupportContainer = RootOccs.addNewComponent(transform)
        SupportContainer.name = SupportContainerName
        SupportContainerComp = SupportContainer.component
        SupportContainerComp.name = SupportContainerName
            

    #creating support component       
    SupportComp = SupportContainer.component.occurrences.addNewComponent(transform)
    #SupportComp.activate()

    if AutomaticBasePlaneXY == False:
        if root.xYConstructionPlane == SPlane:
            Plane = root.xYConstructionPlane
            AutomaticBasePlaneXY == True #using this flag because result is same
            ChamferBottomPlane = False
        else:
            PlaneInput = SupportComp.component.constructionPlanes.createInput()
            PlaneOffsetValue = adsk.core.ValueInput.createByReal(0.0)
            PlaneInput.setByOffset(SPlane,PlaneOffsetValue)
            Plane = SupportComp.component.constructionPlanes.add(PlaneInput)
            Plane.isLightBulbOn = False
            ChamferBottomPlane = True
    else:
        Plane = root.xYConstructionPlane


    BottomSketch = SupportComp.component.sketches.add(Plane)
    
    #Getting distance base plane to create offset plane
    for Line in Curve_sels:
        GotMinDistance = False
        try:
            m1 = app.measureManager.measureMinimumDistance(Line,root.xYConstructionPlane)
        except:
            GotMinDistance = False
        else:
            if 'PlaneLineDistance' not in locals():
                PlaneLineDistance = m1.value
            GotMinDistance = True
            PlaneLineDistance = m1.value if (m1.value < PlaneLineDistance) else PlaneLineDistance
        
        if GotMinDistance == False:
            try:
                ContPoints = Line.geometry.controlPointCount
            except:
                GotMinDistance = False
            else:
                PlaneLineDistance = app.measureManager.measureMinimumDistance(Line.geometry.controlPoints[0],root.xYConstructionPlane).value
                for x in range(0,ContPoints): #if control points has different Z height, take lowest
                    val =  app.measureManager.measureMinimumDistance(Line.geometry.controlPoints[x],root.xYConstructionPlane).value
                    PlaneLineDistance = val if (val < PlaneLineDistance) else PlaneLineDistance
                GotMinDistance = True
        
        if GotMinDistance == False:
            try:
                ContPoints = Line.geometry.asNurbsCurve.controlPointCount
            except:
                GotMinDistance = False
            else:
                PlaneLineDistance = app.measureManager.measureMinimumDistance(Line.geometry.asNurbsCurve.controlPoints[0],root.xYConstructionPlane).value
                for x in range(0,ContPoints):
                    val =  app.measureManager.measureMinimumDistance(Line.geometry.asNurbsCurve.controlPoints[x],root.xYConstructionPlane).value
                    PlaneLineDistance = val if (val < PlaneLineDistance) else PlaneLineDistance
                GotMinDistance = True
    
    
    #check if exists some minimal value
    if ('PlaneLineDistance' in locals()) == False:
        ui.messageBox('Problem with getting distance for sketch plane, Selected line is too complicated.')
        SupportComp.deleteMe()

    PlaneLineDistance += OffsetPlaneZShift
    
    offsetValue = adsk.core.ValueInput.createByReal(PlaneLineDistance)
    PlaneInput = SupportComp.component.constructionPlanes.createInput()
    PlaneInput.setByOffset(root.xYConstructionPlane,offsetValue)
    OffsetSketchPlane = SupportComp.component.constructionPlanes.add(PlaneInput)

    FirstIteration = True
    for Line in Curve_sels:
        
        #creating top sketch
        OffsetSketch = SupportComp.component.sketches.add(OffsetSketchPlane)
        ProjectedLine = OffsetSketch.project(Line)
        ProjectedLineCurve = OffsetSketch.sketchCurves.item(0)
    
        ClosedLoopLine = False
        
        try:
            ProjectedGuidePoint2 = BottomSketch.project(ProjectedLineCurve.startSketchPoint)
        except:
            try:
                ProjectedGuidePoint2 = BottomSketch.project(ProjectedLineCurve.centerSketchPoint)
                ClosedLoopLine = True
            except:
                    try:
                        TempPoint1 = adsk.core.Point3D.create(ProjectedLineCurve.geometry.controlPoints[0].asArray()[0],ProjectedLineCurve.geometry.controlPoints[0].asArray()[1],0)
                        TempPoint1Sketch = OffsetSketch.sketchPoints.add(TempPoint1)
                        ProjectedGuidePoint2 = BottomSketch.project(TempPoint1Sketch)
                        ClosedLoopLine = True
                    except:
                            ui.messageBox('Problem with finding creating point.')

        
            
        GuidePoint2Cords = ProjectedGuidePoint2.item(0).geometry.asArray()
        GuidePoint2AbsZ = ProjectedGuidePoint2.item(0).worldGeometry.asArray()
        
        OffsetDistance = WallThicknessCalc(PlaneLineDistance-GuidePoint2AbsZ[2])/2
        
        #back to topsketch
        Offset1 = OffsetSketch.offset(ProjectedLine,OffsetPoint1,OffsetDistance)
        Offset2 = OffsetSketch.offset(ProjectedLine,OffsetPoint1,-OffsetDistance)
        #Offset1Curve = Offset1.item(0)
        #Offset2Curve = Offset2.item(0)
        OffsetSketch.sketchDimensions.item(0).parameter.value = OffsetDistance
        OffsetSketch.sketchDimensions.item(1).parameter.value = -OffsetDistance     
        #ui.messageBox('Problem with getting distance for sketch plane, Selected line is too complicated.')
        
        #GuidePoint1Cords = ProjectedLineCurve.startSketchPoint.geometry.asArray()
        
        Offset1Curve = OffsetSketch.sketchCurves.item(OffsetSketch.sketchCurves.count-2)
        Offset2Curve = OffsetSketch.sketchCurves.item(OffsetSketch.sketchCurves.count-1)
        
        Offset1Curve.geometricConstraints.item(0).deleteMe()
        Offset2Curve.geometricConstraints.item(0).deleteMe()
        #GuidePointZHeight = app.measureManager.measureMinimumDistance(root.xYConstructionPlane,ProjectedLineCurve.startSketchPoint).value
        #GuidePoint1 = OffsetSketch.sketchPoints.add(GuidePoint1)
        if ClosedLoopLine != True:
            ConnectionLine1 = OffsetSketch.sketchCurves.sketchLines.addByTwoPoints(Offset1Curve.startSketchPoint,Offset2Curve.startSketchPoint)
            ConnectionLine2 = OffsetSketch.sketchCurves.sketchLines.addByTwoPoints(Offset1Curve.endSketchPoint, Offset2Curve.endSketchPoint)
    

        #back to botttom sketch
        ProjectedLineCurve.deleteMe()
        if FirstIteration:
            GuidePoint1 = adsk.core.Point3D.create(GuidePoint2Cords[0],GuidePoint2Cords[1],PlaneLineDistance-GuidePoint2AbsZ[2])
            GuidePoint2 = adsk.core.Point3D.create(GuidePoint2Cords[0],GuidePoint2Cords[1],GuidePoint2Cords[2])
            #GuidePoint2 = BottomSketch.sketchPoints.add(GuidePoint2)
            ProjectedGuidePoint2.item(0).deleteMe()
            GuideLine = BottomSketch.sketchCurves.sketchLines.addByTwoPoints(GuidePoint1,GuidePoint2)
        
        #Sweep
            path = SupportComp.component.features.createPath(GuideLine)
            guide = SupportComp.component.features.createPath(GuideLine)
        sweeps = SupportComp.component.features.sweepFeatures
        if OffsetSketch.profiles.count == 1:
            ProfileToSweep = OffsetSketch.profiles.item(0)
        else:
            try:
                for x in range(0,OffsetSketch.profiles.count): #if there are more profiles in sketch, select that with 2 loops(used in closed lines)
                    if OffsetSketch.profiles.item(x).profileLoops.count ==2:
                        ProfileToSweep = OffsetSketch.profiles.item(x)
                        break
            except:
                ProfileToSweep = OffsetSketch.profiles.item(0)
            else:
                ProfileToSweep = OffsetSketch.profiles.item(0)
        
        sweepInput = sweeps.createInput(OffsetSketch.profiles.item(0), path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
             #sweepInput.guideRail = GuideLine
        sweepInput.profileScaling = adsk.fusion.SweepProfileScalingOptions.SweepProfileScaleOption
        sweep = sweeps.add(sweepInput)
        BottomSketch.isLightBulbOn = True
        
        SweepBody = sweep.bodies.item(0)
        
        #Replace face - if selected base plane is under angle, it is necessarry to do this. Otherwise it doesnt have any impact
        ##find paralel face with XY plane and choose that with lower position
        BottomFace = adsk.core.ObjectCollection.create()
        FaceXYPlaneDistance = PlaneLineDistance
        for face in SweepBody.faces:
            try:
                if face.geometry.isParallelToPlane(OffsetSketchPlane.geometry):
                    if app.measureManager.measureMinimumDistance(face.geometry,root.xYConstructionPlane).value < FaceXYPlaneDistance:
                        BottomFace.clear()
                        BottomFace.add(face)
                        FaceXYPlaneDistance = app.measureManager.measureMinimumDistance(face.geometry,root.xYConstructionPlane).value
            except:
                pass
        ##do replace face
        ReplaceFaceInput = SupportComp.component.features.replaceFaceFeatures.createInput(BottomFace,False,Plane)
        ReplaceFace = SupportComp.component.features.replaceFaceFeatures.add(ReplaceFaceInput)
        
        #Chamfer - this will be a bit tricky
        TopEdges = adsk.core.ObjectCollection.create()
        BottomEdges = adsk.core.ObjectCollection.create()
        for edge in SweepBody.edges: #finding top edges
            Vert1Z = edge.startVertex.geometry.asArray()[2] #getting Z values
            Vert2Z = edge.endVertex.geometry.asArray()[2]
            if (round(Vert1Z,RoundingPrecission) == round(PlaneLineDistance,RoundingPrecission)) and (round(Vert2Z,RoundingPrecission) == round(PlaneLineDistance,RoundingPrecission)):
                TopEdges.add(edge)
            print(ChamferBottomPlane)
            if ChamferBottomPlane == True:
                Vert1Z = round(app.measureManager.measureMinimumDistance(Plane.geometry,edge.startVertex.geometry).value,RoundingPrecission) == 0
                Vert2Z = round(app.measureManager.measureMinimumDistance(Plane.geometry,edge.endVertex.geometry).value,RoundingPrecission) == 0
                print(str(app.measureManager.measureMinimumDistance(Plane.geometry,edge.startVertex.geometry).value) + " " + str(app.measureManager.measureMinimumDistance(Plane.geometry,edge.endVertex.geometry).value) + str(all([Vert1Z,Vert2Z])))
                if all([Vert1Z,Vert2Z]):
                    BottomEdges.add(edge)
        if ClosedLoopLine != True: #removing edges which we do not want to chamfer
            for x in reversed(range(0,TopEdges.count)):
                if (round(TopEdges.item(x).length,RoundingPrecission) == round(ConnectionLine1.length,RoundingPrecission)) or (round(TopEdges.item(x).length,RoundingPrecission) == round(ConnectionLine2.length,RoundingPrecission)) :
                    TopEdges.removeByIndex(x)
    
                    
     
        if TopEdges.count != 2 and (ClosedLoopLine == False):
            #ui.messageBox(str(len(TopEdges)))
            ui.messageBox("Could not recognize 2 edges for top chamfer, please chamfer support geometry manualy")
            TopEdges.clear()

        if BottomEdges.count > 0:
            TopEdges.add(BottomEdges) #i want to create bottom chamfer bulky - all edges in one feature
        chamfers = SupportComp.component.features.chamferFeatures
        ChamferVal = OffsetDistance - (NozzleDiameter_Arg.value /2) - 0.01
        #ui.messageBox(str(OffsetDistance) + " " + str(NozzleDiameter_Arg.value /2) + " " + str(ChamferVal))
        ProblemWithChamfer = False
        ValuesBeenChangedChanfer = False
        print(len(TopEdges))
        for edge in TopEdges:
            print("loop")
            try: #some "wild" nurbs can have problems with chamfer  
                edgeCollection = adsk.core.ObjectCollection.create()
                edgeCollection.add(edge)
                if type(edge) == type(edgeCollection):
                    edgeCollection = edge
                chamferInput = chamfers.createInput(edgeCollection, True)
                chamferInput.setToTwoDistances(adsk.core.ValueInput.createByReal(ChamferVal),adsk.core.ValueInput.createByReal(ChamferVal))
                chamfer = chamfers.add(chamferInput)
            except:
                try: #trying to reduce chamfer value to 1/2
                    chamfers.item(chamfers.count-1).deleteMe()
                    chamferInput.setToTwoDistances(adsk.core.ValueInput.createByReal(ChamferVal/2),adsk.core.ValueInput.createByReal(ChamferVal/2))
                    chamfer = chamfers.add(chamferInput)
                except:
                    ProblemWithChamfer = True
                else:
                    ValuesBeenChangedChanfer = True
            
        if ProblemWithChamfer == True:
            ui.messageBox("Problem with atleast one chamfer creation, check features history and try to manualy change distance value.")
        if ValuesBeenChangedChanfer == True:
            ui.messageBox("Some chamfer values has been reduced, please check contact surface.")
        if FirstIteration == False:
            ProjectedGuidePoint2.item(0).deleteMe()
        
        FirstIteration = False
       

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('BridgeSupportGeometry_ID')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('BridgeSupportGeometry_ID')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	