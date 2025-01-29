#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

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
        lines = sketch.sketchCurves.sketchLines
        lines.addByTwoPoints(adsk.core.Point3D.create(0, 1, 0), adsk.core.Point3D.create(1, 1, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(1, 1, 0), adsk.core.Point3D.create(1, 0, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(1, 0, 0), adsk.core.Point3D.create(2, 0, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(2, 0, 0), adsk.core.Point3D.create(2, 1, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(2, 1, 0), adsk.core.Point3D.create(3, 1, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(3, 1, 0), adsk.core.Point3D.create(3, 2, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(3, 2, 0), adsk.core.Point3D.create(2, 2, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(2, 2, 0), adsk.core.Point3D.create(2, 3, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(2, 3, 0), adsk.core.Point3D.create(1, 3, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(1, 3, 0), adsk.core.Point3D.create(1, 2, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(1, 2, 0), adsk.core.Point3D.create(0, 2, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(0, 2, 0), adsk.core.Point3D.create(0, 1, 0))
        prof = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(1)
        extInput.setDistanceExtent(False, distance)
        ext = extrudes.add(extInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
