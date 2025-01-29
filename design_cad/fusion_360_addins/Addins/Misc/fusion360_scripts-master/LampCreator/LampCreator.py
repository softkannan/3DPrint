#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

DESIGN_RADIUS = 15 # DO NOT CHANGE
MASTER_RADIUS = 15
THICKNESS = .6

def run(context):
    ui = None
    try:
        circumference = 2 * (math.pi * MASTER_RADIUS)

        app = adsk.core.Application.get()
        
        ui  = app.userInterface

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = app.activeProduct

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create a new sketch on the xy plane.
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        xzPlane = rootComp.xZConstructionPlane
        yzPlane = rootComp.yZConstructionPlane

        extrudes = rootComp.features.extrudeFeatures
        moveFeats = rootComp.features.moveFeatures
        combines = rootComp.features.combineFeatures

        occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = "Sconce"

        mainComp = occ.component

        # Load the leaf DXF
        importMgr = app.importManager
        dxfoptions = importMgr.createDXF2DImportOptions("C:\\Users\\dan\\Documents\\leaf.dxf", xzPlane)
        importMgr.importToTarget(dxfoptions, rootComp)

        results = dxfoptions.results
        leafSketch = adsk.fusion.Sketch.cast(results[0])
        leafSketch.name = "leaf"

        # Create ref circles

        wallRefCircleSketch = sketches.add(xyPlane)
        wallRefCenter = adsk.core.Point3D.create(0, MASTER_RADIUS, 0)
        circles = wallRefCircleSketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(wallRefCenter, MASTER_RADIUS)

        sideRefCircleSketch = sketches.add(yzPlane)
        sideRefCenter = adsk.core.Point3D.create(0, MASTER_RADIUS, 0)
        circles = sideRefCircleSketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(sideRefCenter, MASTER_RADIUS)

        # Create horizontal supports

        support1center = adsk.core.Point3D.create(0, 0, MASTER_RADIUS/5)
        support2center = adsk.core.Point3D.create(0, 0, MASTER_RADIUS/1.5)

        support1rad = math.sqrt(pow(MASTER_RADIUS, 2) - pow((MASTER_RADIUS-support1center.z), 2))
        support2rad = math.sqrt(pow(MASTER_RADIUS, 2) - pow((MASTER_RADIUS-support2center.z), 2))

        bottomSupport = addHorizontalArc(mainComp, support1center, support1rad-5, support1rad)
        topSupport = addHorizontalArc(mainComp, support2center, support2rad-4, support2rad)

        bottomSupport.name = "bottom_support"
        topSupport.name = "top_support"

        horizSupports = adsk.core.ObjectCollection.create()
        horizSupports.add(bottomSupport.bRepBodies[0])
        horizSupports.add(topSupport.bRepBodies[0])

        # Create vertical components

        verts = []
        outer_verts = adsk.core.ObjectCollection.create() 
        inner_verts = adsk.core.ObjectCollection.create()

        for i in range(9):
            bodies = addVerticalArc(rootComp, "vert_" + str(i))

            transform = adsk.core.Matrix3D.create()
            rotation = adsk.core.Matrix3D.create()
            rotation.setToRotation(math.radians((i*20)+10), adsk.core.Vector3D.create(0,1,0), adsk.core.Point3D.create(0,0,0))
            transform.transformBy(rotation)

            occ = mainComp.occurrences.addNewComponent(transform)
            occ.component.name =  "vert_" + str(i)
            objects = adsk.core.ObjectCollection.create() 
            
            bodies[0].moveToComponent(occ)
            bodies[1].moveToComponent(occ)

            objects.add(occ.component.bRepBodies[0])
            objects.add(occ.component.bRepBodies[1])

            moveInput = occ.component.features.moveFeatures.createInput(objects, transform)
            occ.component.features.moveFeatures.add(moveInput)

            outer_verts.add(occ.component.bRepBodies[0])
            inner_verts.add(occ.component.bRepBodies[1])

        # combine outers and inner verts

        combineInput = combines.createInput(topSupport.bRepBodies[0], outer_verts)
        combineInput.isKeepToolBodies = True
        combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combines.add(combineInput)

        combineInput = combines.createInput(bottomSupport.bRepBodies[0], outer_verts)
        combineInput.isKeepToolBodies = True
        combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combines.add(combineInput)

        for i in range(inner_verts.count):
            inner = inner_verts[i]
            combineInput = combines.createInput(inner, horizSupports)
            combineInput.isKeepToolBodies = True
            combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            res = adsk.core.ObjectCollection.create()
            for b in combines.add(combineInput).bodies:
                res.add(b)

            combineInput = combines.createInput(outer_verts[i], res)
            combineInput.isKeepToolBodies = False
            combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            feat = combines.add(combineInput)
            verts.append(feat.bodies[0])          

        # Get reference positions for leaves
        evenPoints = getLeafPositions(rootComp, design, 30)
        oddPoints = getLeafPositions(rootComp, design, 65)

        leafProfile = leafSketch.profiles.item(0)
        thickness = adsk.core.ValueInput.createByReal(THICKNESS)

        leafOrigin = adsk.core.Point3D.create(0,0,0)
        rotationAdd = 0

        designToSizeRatio = MASTER_RADIUS / DESIGN_RADIUS 

        leafTilt = []
        leafScale = []
        leafId = 0
        for i in range(9):
            if (i % 2) == 0:
                leafPoints = evenPoints
                leafTilt = [15, 35, 55, 65, 75, 85]
                leafScale = [.8, 1.2, 1.3, 1.3, 1.2, .9]
            else:
                leafPoints = oddPoints
                leafTilt = [25, 40, 57, 70, 80, 90]
                leafScale = [1, 1.3, 1.3, 1.3, 1.1, .7]

            for s in range(len(leafScale)):
                leafScale[s] = leafScale[s] * designToSizeRatio

            l = 0
            leavesForVert = adsk.core.ObjectCollection.create()

            for pt in leafPoints:

                newLeaf = copyAndScaleSketch(rootComp, leafSketch, leafScale[l])
                addSlot(newLeaf)

                feat = extrudes.addSimple(newLeaf.profiles[0], thickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                feat.bodies[0].name = "leaf_" + str(leafId)
                leafId = leafId + 1

                transform = adsk.core.Matrix3D.create()

                rotation0 = adsk.core.Matrix3D.create()
                rotation0.setToRotation(math.radians(leafTilt[l]), adsk.core.Vector3D.create(0,0,1), adsk.core.Point3D.create(0,0,0))
                transform.transformBy(rotation0)

                move = adsk.core.Matrix3D.create()
                move.translation = leafOrigin.vectorTo(pt)
                transform.transformBy(move)
                
                bodyCollection = adsk.core.ObjectCollection.create()
                bodyCollection.add(feat.bodies[0])

                moveFeatureInput = moveFeats.createInput(bodyCollection, transform)
                moveFeats.add(moveFeatureInput)
                
                rotation1 = adsk.core.Matrix3D.create()
                rotation1.setToRotation(math.radians((i*20)+10), adsk.core.Vector3D.create(0,1,0), adsk.core.Point3D.create(0,0,0))
                transform.transformBy(rotation1)

                leafComp = mainComp.occurrences.addNewComponent(transform)
                leafComp.component.name = feat.bodies[0].name
                feat.bodies[0].moveToComponent(leafComp)

                compCollection = adsk.core.ObjectCollection.create()
                compCollection.add(leafComp.component.bRepBodies[0])

                rotateBodies(leafComp.component, compCollection, adsk.core.Vector3D.create(0,1,0), adsk.core.Point3D.create(0,0,0), (i*20)+10)

                leavesForVert.add(leafComp.component.bRepBodies[0])  

                l = l + 1
            
            combineInput = combines.createInput(verts[i], leavesForVert)
            combineInput.isKeepToolBodies = True
            combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            combines.add(combineInput)

        CenterAndShowInWindowAllVisibleObjects(app)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createComponent(target, position, body):
    transform = adsk.core.Matrix3D.create()
    transform.translation = position

    objects = adsk.core.ObjectCollection.create() 

    occ = target.occurrences.addNewComponent(transform)
    occ.component.name = body.name

    body.moveToComponent(occ)
    objects.add(occ.component.bRepBodies[0])
    moveInput = occ.component.features.moveFeatures.createInput(objects, transform)
    occ.component.features.moveFeatures.add(moveInput)

    return occ.component

def addSlot(sketch):
    backRight = adsk.core.Point3D.create(-1,-(THICKNESS/2),0)
    backLeft = adsk.core.Point3D.create(-1,(THICKNESS/2),0)
    frontRight = adsk.core.Point3D.create(.8,-(THICKNESS/2),0)
    frontLeft = adsk.core.Point3D.create(.8,(THICKNESS/2),0)

    lines = sketch.sketchCurves.sketchLines
    line0 = lines.addByTwoPoints(backRight, frontRight)
    line0.isConstruction = False
    line1 = lines.addByTwoPoints(backLeft, frontLeft)
    line1.isConstruction = False
    line2 = lines.addByTwoPoints(frontRight, frontLeft)
    line2.isConstruction = False

def copyAndScaleSketch(rootComp, sourceSketch, scale):

    sketches = rootComp.sketches
    plane = rootComp.xZConstructionPlane

    sketch = sketches.add(plane)
    sketches = adsk.core.ObjectCollection.create()
    sketches.add(sketch)

    entities = adsk.core.ObjectCollection.create()
    for point in sourceSketch.sketchPoints:
        entities.add(point)
    for curve in sourceSketch.sketchCurves:
        entities.add(curve)

    transform = adsk.core.Matrix3D.create()

    sourceSketch.copy(entities, transform, sketch)

    scaleFactor = adsk.core.ValueInput.createByReal(scale)
    scaleInput = rootComp.features.scaleFeatures.createInput(sketches, sketch.sketchPoints[0], scaleFactor)

    rootComp.features.scaleFeatures.add(scaleInput)

    return sketch


def getLeafPositions(rootComp, des, offset):
    center = adsk.core.Point3D.create(0, MASTER_RADIUS, 0)

    sketches = rootComp.sketches
    plane = rootComp.xYConstructionPlane
    extrudes = rootComp.features.extrudeFeatures
    circumference = 2 * math.pi * MASTER_RADIUS

    step = ((((circumference * 10) / 360) * 150) / 7)

    points = []

    unitsMgr = des.unitsManager

    sketch = sketches.add(plane)
    sketch.name = "vert_ref"

    outerRadPoint = adsk.core.Point3D.create(0,-1,0)

    arcs = sketch.sketchCurves.sketchArcs
    arc1 = arcs.addByCenterStartSweep(center, outerRadPoint, math.radians(150))

    crv = sketch.sketchCurves[0].worldGeometry
    eva = crv.evaluator
    returnValue, startPoint, endPoint = eva.getEndPoints()

    #start parameter
    returnValue, start_prm = eva.getParameterAtPoint(startPoint)
    
    for i in range (1, 7):

        mm = unitsMgr.convert((i * step) + offset, "mm", unitsMgr.internalUnits)

        #1mm Parameter
        returnValue, leng_1mm_prm = eva.getParameterAtLength(start_prm, mm)
        
        #1mm point
        returnValue, pnt3d = eva.getPointAtParameter(leng_1mm_prm)
        
        #to sketchPoints
        points.append(pnt3d)
        skt_point = sketch.sketchPoints.add(pnt3d)

    return points

def addVerticalArc(rootComp, name):
    center = adsk.core.Point3D.create(0, MASTER_RADIUS, 0)
    sketches = rootComp.sketches
    plane = rootComp.xYConstructionPlane
    extrudes = rootComp.features.extrudeFeatures

    sketch = sketches.add(plane)
    sketch.name = name

    innerRadPoint = adsk.core.Point3D.create(0,-2,0)
    outerRadPoint = adsk.core.Point3D.create(0,2,0)
    midRadPoint = adsk.core.Point3D.create(0,((outerRadPoint.y-innerRadPoint.y)/3),0)

    arcs = sketch.sketchCurves.sketchArcs
    arc1 = arcs.addByCenterStartSweep(center, outerRadPoint, math.radians(150))
    arc2 = arcs.addByCenterStartSweep(center, innerRadPoint, math.radians(150))
    arc3 = arcs.addByCenterStartSweep(center, midRadPoint, math.radians(150))

    lines = sketch.sketchCurves.sketchLines
    lines.addByTwoPoints(arc1.startSketchPoint, arc2.startSketchPoint)
    lines.addByTwoPoints(arc1.endSketchPoint, arc2.endSketchPoint)

    profileCount = sketch.profiles.count
    thickness = adsk.core.ValueInput.createByReal(THICKNESS/2)
    negThickness = adsk.core.ValueInput.createByReal(-(THICKNESS / 2))

    bodies = adsk.core.ObjectCollection.create()

    prof = sketch.profiles.item(0)

    frontExtrusion = extrudes.addSimple(prof, thickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    rearExtrusion = extrudes.addSimple(prof, negThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    feature = joinBodies(rootComp.features.combineFeatures, frontExtrusion.bodies.item(0), rearExtrusion.bodies.item(0))
    feature.bodies[0].name = name + "_outer"
    bodies.add(feature.bodies[0])

    prof = sketch.profiles.item(1)

    frontExtrusion = extrudes.addSimple(prof, thickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    rearExtrusion = extrudes.addSimple(prof, negThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    feature = joinBodies(rootComp.features.combineFeatures, frontExtrusion.bodies.item(0), rearExtrusion.bodies.item(0))
    feature.bodies[0].name = name + "_inner"
    bodies.add(feature.bodies[0])

    return bodies


def scaleBodies(root, bodies, basePoint, scaleX, scaleY, scaleZ):
    scaleFactorX = adsk.core.ValueInput.createByReal(scaleX)
    scaleFactorY = adsk.core.ValueInput.createByReal(scaleY)
    scaleFactorZ = adsk.core.ValueInput.createByReal(scaleZ)
    scaleInput = root.features.scaleFeatures.createInput(bodies, basePoint, scaleFactorX)
    scaleInput.setToNonUniform(scaleFactorX, scaleFactorY, scaleFactorZ)

    return root.features.scaleFeatures.add(scaleInput)

def translateBodies(root, body, rotationVector, translation):
    translation = adsk.core.Matrix3D.create()
    rotation.setToRotation(math.radians(degrees), rotationVector, origin)
    transform.transformBy(rotation)

    moveInput = root.features.moveFeatures.createInput(bodies, transform)
    return root.features.moveFeatures.add(moveInput)

def rotateBodies(root, bodies, rotationVector, origin, degrees):
    transform = adsk.core.Matrix3D.create()
    rotation = adsk.core.Matrix3D.create()
    rotation.setToRotation(math.radians(degrees), rotationVector, origin)
    transform.transformBy(rotation)

    moveInput = root.features.moveFeatures.createInput(bodies, transform)
    return root.features.moveFeatures.add(moveInput)

def joinBodies(combines, bodyOne, bodyTwo):

    tools = adsk.core.ObjectCollection.create()
    tools.add(bodyTwo)

    combineInput = combines.createInput(bodyOne, tools)
    combineInput.isKeepToolBodies = False
    combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation

    return combines.add(combineInput)

def addHorizontalArc(rootComp, center, innerRad, outerRad):
    sketches = rootComp.sketches
    plane = rootComp.xZConstructionPlane
    extrudes = rootComp.features.extrudeFeatures

    sketch = sketches.add(plane)

    # innerRadPoint = adsk.core.Point3D.create(innerRad, center.y, center.z)
    # outerRadPoint = adsk.core.Point3D.create(outerRad, center.y, center.z)

    origin = adsk.core.Point3D.create(0, 0, 0)
    innerRadPoint = adsk.core.Point3D.create(innerRad, 0, 0)
    outerRadPoint = adsk.core.Point3D.create(outerRad, 0, 0)

    arcs = sketch.sketchCurves.sketchArcs
    arc1 = arcs.addByCenterStartSweep(origin, outerRadPoint, math.radians(180))
    arc2 = arcs.addByCenterStartSweep(origin, innerRadPoint, math.radians(180))

    lines = sketch.sketchCurves.sketchLines
    line1 = lines.addByTwoPoints(arc1.startSketchPoint, arc2.startSketchPoint)
    line2 = lines.addByTwoPoints(arc1.endSketchPoint, arc2.endSketchPoint)

    prof = sketch.profiles.item(sketch.profiles.count-1)
    thickness = adsk.core.ValueInput.createByReal(THICKNESS)
    feature = extrudes.addSimple(prof, thickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    positionalVector = adsk.core.Vector3D.create(center.x, center.z, center.y)

    return createComponent(rootComp, positionalVector, feature.bodies[0])

def CenterAndShowInWindowAllVisibleObjects(app :adsk.core.Application) -> bool:
    viewPort :adsk.core.Viewport = app.activeViewport

    if (not viewPort):
        return False

    camera :adsk.core.Camera = viewPort.camera

    if (not camera):
        return False

    camera.isFitView =  True
    viewPort.camera = camera

    return True