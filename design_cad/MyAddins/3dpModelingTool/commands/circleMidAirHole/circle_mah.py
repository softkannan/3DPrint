import adsk.core, adsk.fusion, adsk.cam, traceback
from ...lib import fusion360utils as futil
import math
app = adsk.core.Application.get()
ui = app.userInterface

def create_circle_mah_tool(component, layer_thick, large_hole, large_depth, small_hole, small_depth):
    # get basic object
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root = design.rootComponent
    extrudes = component.features.extrudeFeatures
    combines = component.features.combineFeatures
    timelineGroups = design.timeline.timelineGroups
    # large hole
    sketch_large = component.sketches.add(root.xYConstructionPlane)
    center = adsk.core.Point3D.create(0, 0, 0)
    radius = large_hole / 2.0
    sketch_large.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
    prof = sketch_large.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(large_depth)
    body_large = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body_large = body_large.bodies.item(0)
    startIndex = sketch_large.timelineObject.index
    # small hole
    sketch_small = component.sketches.add(root.xYConstructionPlane)
    center = adsk.core.Point3D.create(0, 0, 0)
    radius = small_hole / 2.0
    sketch_small.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
    prof = sketch_small.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(small_depth + large_depth)
    body_small = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body_small = body_small.bodies.item(0)
    # first
    sketch_first = component.sketches.add(root.xYConstructionPlane)
    buf1 = small_hole / 2.0
    buf2 = math.sqrt(large_hole**2 / 4.0 - buf1**2)
    p0 = adsk.core.Point3D.create(0, 0, 0)
    p1 = adsk.core.Point3D.create(buf2, buf1, 0)
    p2 = adsk.core.Point3D.create(buf2, -buf1, 0)
    p3 = adsk.core.Point3D.create(-buf2, -buf1, 0)
    p4 = adsk.core.Point3D.create(-buf2, buf1, 0)
    angle = math.atan(buf2 / buf1) * 2.0
    sketch_first.sketchCurves.sketchArcs.addByCenterStartSweep(p0, p1, -angle)
    sketch_first.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    sketch_first.sketchCurves.sketchArcs.addByCenterStartSweep(p0, p3, -angle)
    sketch_first.sketchCurves.sketchLines.addByTwoPoints(p4, p1)
    prof = sketch_first.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(layer_thick * 1.0 + large_depth)
    body_first = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body_first = body_first.bodies.item(0)
    # second
    sketch_second = component.sketches.add(root.xYConstructionPlane)
    buf1 = small_hole / 2.0
    p1 = adsk.core.Point3D.create(buf1, buf1, 0)
    p2 = adsk.core.Point3D.create(buf1, -buf1, 0)
    p3 = adsk.core.Point3D.create(-buf1, -buf1, 0)
    p4 = adsk.core.Point3D.create(-buf1, buf1, 0)
    sketch_second.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    sketch_second.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    sketch_second.sketchCurves.sketchLines.addByTwoPoints(p3, p4)
    sketch_second.sketchCurves.sketchLines.addByTwoPoints(p4, p1)
    prof = sketch_second.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(layer_thick * 2.0 + large_depth)
    body_second = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body_second = body_second.bodies.item(0)
    # join
    join_body = body_large
    join_tool = adsk.core.ObjectCollection.create()
    join_tool.add(body_small)
    join_tool.add(body_first)
    join_tool.add(body_second)
    combineInput = combines.createInput(join_body, join_tool)
    combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combineInput.isKeepToolBodies = False
    combineInput.isNewComponent = False
    combineFeat = combines.add(combineInput)
    endIndex = combineFeat.timelineObject.index
    # timeline
    group = timelineGroups.add(startIndex, endIndex)
    group.name = 'Circle_mid_air_hole cut tool'
    return join_body

def cut_circle_mah_by_point(target_body, tool_body, point):
    # target data
    wx = point.worldGeometry.x
    wy = point.worldGeometry.y
    wz = point.worldGeometry.z
    x_dir = point.parentSketch.xDirection
    y_dir = point.parentSketch.yDirection
    # calc norm
    nx = x_dir.y * y_dir.z - x_dir.z * y_dir.y
    ny = x_dir.z * y_dir.x - x_dir.x * y_dir.z
    nz = x_dir.x * y_dir.y - x_dir.y * y_dir.x
    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx = nx / ln
    ny = ny / ln
    nz = nz / ln

    # preparation
    component = target_body.parentComponent
    moveFeats = component.features.moveFeatures
    combines = component.features.combineFeatures
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    timelineGroups = design.timeline.timelineGroups
    copy = component.features.copyPasteBodies.add(tool_body)
    startIndex = copy.timelineObject.index
    copy = copy.bodies.item(0)
    cut_tool = adsk.core.ObjectCollection.create()
    cut_tool.add(copy)
    # reverse
    rotTrans = adsk.core.Matrix3D.create()
    rotTrans.setToRotateTo(adsk.core.Vector3D.create(0,0,1), adsk.core.Vector3D.create(0,0,-1))
    moveFeatureInput = moveFeats.createInput(cut_tool, rotTrans)
    moveFeats.add(moveFeatureInput)
    # rotate
    if nx!=0 or ny!=0 or nz!=1:
        rotTrans = adsk.core.Matrix3D.create()
        rotTrans.setToRotateTo(adsk.core.Vector3D.create(0,0,1), adsk.core.Vector3D.create(nx,ny,nz))
        moveFeatureInput = moveFeats.createInput(cut_tool, rotTrans)
        moveFeats.add(moveFeatureInput)
    # transform
    if wx!=0 or wy!=0 or wz!=0:
        moveTrans = adsk.core.Matrix3D.create()
        vector = adsk.core.Vector3D.create(wx, wy, wz)
        moveTrans.translation = vector
        moveFeatureInput = moveFeats.createInput(cut_tool, moveTrans)
        moveFeats.add(moveFeatureInput)
    # cut
    combineInput = combines.createInput(target_body, cut_tool)
    combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combineInput.isKeepToolBodies = False
    combineInput.isNewComponent = False
    combineFeat = combines.add(combineInput)
    endIndex = combineFeat.timelineObject.index
    # timeline
    group = timelineGroups.add(startIndex, endIndex)
    group.name = 'Circle_mid_air_hole move and cut'

def cut_circle_mah_by_3dcircle(target_body, tool_body, edge):
    circle = adsk.core.Circle3D.cast(edge)
    # target data
    wx = circle.center.x
    wy = circle.center.y
    wz = circle.center.z
    nx = circle.normal.x
    ny = circle.normal.y
    nz = circle.normal.z

    # preparation
    component = target_body.parentComponent
    moveFeats = component.features.moveFeatures
    combines = component.features.combineFeatures
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    timelineGroups = design.timeline.timelineGroups
    copy = component.features.copyPasteBodies.add(tool_body)
    startIndex = copy.timelineObject.index
    copy = copy.bodies.item(0)
    cut_tool = adsk.core.ObjectCollection.create()
    cut_tool.add(copy)
    # rotate
    if nx!=0 or ny!=0 or nz!=1:
        rotTrans = adsk.core.Matrix3D.create()
        rotTrans.setToRotateTo(adsk.core.Vector3D.create(0,0,1), adsk.core.Vector3D.create(nx,ny,nz))
        moveFeatureInput = moveFeats.createInput(cut_tool, rotTrans)
        moveFeats.add(moveFeatureInput)
    # transform
    if wx!=0 or wy!=0 or wz!=0:
        moveTrans = adsk.core.Matrix3D.create()
        vector = adsk.core.Vector3D.create(wx, wy, wz)
        moveTrans.translation = vector
        moveFeatureInput = moveFeats.createInput(cut_tool, moveTrans)
        moveFeats.add(moveFeatureInput)
    # cut
    combineInput = combines.createInput(target_body, cut_tool)
    combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combineInput.isKeepToolBodies = False
    combineInput.isNewComponent = False
    combineFeat = combines.add(combineInput)
    endIndex = combineFeat.timelineObject.index
    # timeline
    group = timelineGroups.add(startIndex, endIndex)
    group.name = 'Circle_mid_air_hole move and cut'
