#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        xzPlane = rootComp.xZConstructionPlane
        sketch1 = sketches.add(xyPlane)
        sketch2 = sketches.add(xzPlane)
        points = adsk.core.ObjectCollection.create()
        d = math.pi / 180
        for i in range(180, 1443, 3):
            x = math.cos(i * d) * i / 180
            y = math.sin(i * d) * i / 180
            z = (1440 - i) / 1260 * 10
            points.add(adsk.core.Point3D.create(x, y, z))
        splines = sketch1.sketchCurves.sketchFittedSplines
        spline = splines.add(points)
        circles = sketch2.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(8, 0, 0), 1)
        path = rootComp.features.createPath(spline)
        prof = sketch2.profiles.item(0)
        sweeps = rootComp.features.sweepFeatures
        sweepInput = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweepInput.taperAngle = adsk.core.ValueInput.createByReal(0)
        sweepInput.twistAngle = adsk.core.ValueInput.createByReal(0)
        sweep = sweeps.add(sweepInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
