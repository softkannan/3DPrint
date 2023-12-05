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
        sketch1 = sketches.add(xyPlane)
        arcs = sketch1.sketchCurves.sketchArcs
        d = math.pi / 180
        cd = 60
        for i in range(6):
            cx = math.cos(i * 60 * d) * 5
            cy = math.sin(i * 60 * d) * 5
            cp = adsk.core.Point3D.create(cx, cy, 0)
            sx = cx + math.cos((i * 60 - cd) * d) * 5
            sy = cy + math.sin((i * 60 - cd) * d) * 5
            sp = adsk.core.Point3D.create(sx, sy, 0)
            arcs.addByCenterStartSweep(cp, sp, cd * 2 / 180 * math.pi)
        sketch2 = sketches.add(xyPlane)
        circles = sketch2.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 1), 5)
        extrudes = rootComp.features.extrudeFeatures
        prof1 = sketch1.profiles.item(0)
        extInput = extrudes.createInput(prof1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(1)
        extInput.setDistanceExtent(False, distance)
        ext = extrudes.add(extInput)
        prof2 = sketch2.profiles.item(0)
        extInput = extrudes.createInput(prof2, adsk.fusion.FeatureOperations.CutFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(-0.5)
        extInput.setDistanceExtent(False, distance)
        ext = extrudes.add(extInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
