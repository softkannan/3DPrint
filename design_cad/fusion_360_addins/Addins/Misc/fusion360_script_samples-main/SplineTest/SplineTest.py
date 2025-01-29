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
        sketch = sketches.add(xyPlane)
        points1 = adsk.core.ObjectCollection.create()
        points2 = adsk.core.ObjectCollection.create()
        for i in range(100):
            x = i / 100
            y = x ** (2 / 3) + (1 - x ** 2) ** (1 / 2)
            points1.add(adsk.core.Point3D.create(x * 5, y * 4, 0))
            points2.add(adsk.core.Point3D.create(-x * 5, y * 4, 0))
        for i in range(100, -1, -1):
            x = i / 100
            y = x ** (2 / 3) - (1 - x ** 2) ** (1 / 2)
            points1.add(adsk.core.Point3D.create(x * 5, y * 4, 0))
            points2.add(adsk.core.Point3D.create(-x * 5, y * 4, 0))
        splines = sketch.sketchCurves.sketchFittedSplines
        splines.add(points1)
        splines.add(points2)
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(1)
        extInput.setDistanceExtent(False, distance)
        ext = extrudes.add(extInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
