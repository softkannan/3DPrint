#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:

        masterRadius = 37.5

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

        extrudes = rootComp.features.extrudeFeatures
        moveFeats = rootComp.features.moveFeatures
        combines = rootComp.features.combineFeatures

        horizBodiesDict = {}
        horizOuterBodies = adsk.core.ObjectCollection.create()
        vertBodies = adsk.core.ObjectCollection.create()

        materialThickness = .3175
        thickness = adsk.core.ValueInput.createByReal(materialThickness)
        halfThickness = adsk.core.ValueInput.createByReal(materialThickness / 2)
        negHalfThickness = adsk.core.ValueInput.createByReal(-(materialThickness / 2))

        for h in range(-10, 11):

            sketchHeight = h*3.3

            sketch = sketches.add(xzPlane)

            center = adsk.core.Point3D.create(0, 0, sketchHeight)

            radiusForHeight = math.sqrt(pow(masterRadius, 2) - pow(sketchHeight, 2)) + 0.3
            innerRad = radiusForHeight - 2.5
            midRad = ((radiusForHeight - innerRad) / 2) + innerRad

            circles = sketch.sketchCurves.sketchCircles
            circles.addByCenterRadius(center, radiusForHeight)
            circles.addByCenterRadius(center, midRad)
            circles.addByCenterRadius(center, innerRad)

            horizBodiesDict[str(h)] = {}

            for i in range(0, sketch.profiles.count-1):
                prof = sketch.profiles.item(i)
                extrudeFront = extrudes.addSimple(prof, halfThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                extrudeBack = extrudes.addSimple(prof, negHalfThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

                feature = joinBodies(combines, extrudeFront.bodies.item(0), extrudeBack.bodies.item(0))

                body = feature.bodies.item(0)
                if i > 0:
                    horizBodiesDict[str(h)]['inner'] = body
                    body.name = "horiz_inner_" + str(h)
                else:
                    horizBodiesDict[str(h)]['outer'] = body
                    horizOuterBodies.add(body)
                    body.name = "horiz_outer_" + str(h)

        for v in range(0, 16):

            sketch = sketches.add(xyPlane)
            circles = sketch.sketchCurves.sketchCircles
            circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), masterRadius)
            circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), masterRadius-2.5)

            all = adsk.core.ObjectCollection.create()
            for c in sketch.sketchCurves:
                all.add(c)
            for p in sketch.sketchPoints:
                all.add(p)

            origin = sketch.origin
            origin.transformBy(sketch.transform)
            mat = adsk.core.Matrix3D.create()
            mat.setToRotation((math.pi / 16) * v, adsk.core.Vector3D.create(0,1,0), origin)
            sketch.move(all, mat)

            prof = sketch.profiles.item(0)

            extrudeFront = extrudes.addSimple(prof, halfThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrudeBack = extrudes.addSimple(prof, negHalfThickness, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            feature = joinBodies(combines, extrudeFront.bodies.item(0), extrudeBack.bodies.item(0))

            feature.bodies.item(0).name = "vert_" + str(v)
            vertBodies.add(feature.bodies.item(0))


        for vert in vertBodies:
            combineInput = combines.createInput(vert, horizOuterBodies)
            combineInput.isKeepToolBodies = True
            combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            combines.add(combineInput)

        for i in horizBodiesDict:
            combineInput = combines.createInput(horizBodiesDict[i]['inner'], vertBodies)
            combineInput.isKeepToolBodies = True
            combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            feature = combines.add(combineInput)

            tool_bodies = adsk.core.ObjectCollection.create()
            for body in feature.bodies:
                tool_bodies.add(body)

            combineInput = combines.createInput(horizBodiesDict[i]['outer'], tool_bodies)
            combineInput.isKeepToolBodies = False
            combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            combines.add(combineInput)

        CenterAndShowInWindowAllVisibleObjects(app)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def joinBodies(combines, bodyOne, bodyTwo):

    tools = adsk.core.ObjectCollection.create()
    tools.add(bodyTwo)

    combineInput = combines.createInput(bodyOne, tools)
    combineInput.isKeepToolBodies = False
    combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    return combines.add(combineInput)

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