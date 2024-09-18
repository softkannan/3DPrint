import adsk.core, adsk.fusion, adsk.cam, traceback
from ...lib import fusion360utils as futil
import math
from ...lib import mathutil as mutil 
app = adsk.core.Application.get()
ui = app.userInterface

def get_face_formula(face):
    face = adsk.fusion.BRepFace.cast(face)
    plane = adsk.core.Plane.cast(face.geometry)
    norm = plane.normal
    if face.isParamReversed:
        norm = adsk.core.Vector3D.create(-norm.x, -norm.y, -norm.z)
    futil.log('bottom face norm:({0},{1},{2}), param reserved:{3}'.format(norm.x, norm.y, norm.z, face.isParamReversed))
    return norm

def get_vector_by_point(base_norm, point):
    # target data
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

    # calcurate vector
    delta = nx * base_norm.x + ny * base_norm.y + nz * base_norm.z
    vx = base_norm.x - delta * nx
    vy = base_norm.y - delta * ny
    vz = base_norm.z - delta * nz
    vl = math.sqrt(vx**2 + vy**2 + vz**2)
    vx = -vx / vl
    vy = -vy / vl
    vz = -vz / vl
    vector = adsk.core.Vector3D.create(vx, vy, vz)
    return vector

def get_vector_by_3dcircle(base_norm, edge):
    circle = adsk.core.Circle3D.cast(edge)
    # target data
    nx = -circle.normal.x
    ny = -circle.normal.y
    nz = -circle.normal.z

    # calcurate vector
    delta = nx * base_norm.x + ny * base_norm.y + nz * base_norm.z
    vx = base_norm.x - delta * nx
    vy = base_norm.y - delta * ny
    vz = base_norm.z - delta * nz
    vl = math.sqrt(vx**2 + vy**2 + vz**2)
    vx = -vx / vl
    vy = -vy / vl
    vz = -vz / vl
    vector = adsk.core.Vector3D.create(vx, vy, vz)
    return vector

def cut_cvh_tool_by_ah(component, sketch, rotth, startIndex, diameter, depth, a, h):
    # get basic object
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    timelineGroups = design.timeline.timelineGroups
    root = design.rootComponent
    extrudes = component.features.extrudeFeatures
    # sketch
    buf1 = diameter / 2.0 * math.sin(a)
    buf2 = diameter / 2.0 * math.cos(a)
    buf3 = diameter / 2.0 + h
    buf4 = buf1 - (buf3 - buf2) / math.tan(a)
    p0 = adsk.core.Point3D.create(0, 0, 0)
    p1 = adsk.core.Point3D.create(buf1 * math.cos(rotth) - buf2 * math.sin(rotth), buf1 * math.sin(rotth) + buf2 * math.cos(rotth), 0)
    p2 = adsk.core.Point3D.create(buf4 * math.cos(rotth) - buf3 * math.sin(rotth), buf4 * math.sin(rotth) + buf3 * math.cos(rotth), 0)
    p3 = adsk.core.Point3D.create(-buf4 * math.cos(rotth) - buf3 * math.sin(rotth), -buf4 * math.sin(rotth) + buf3 * math.cos(rotth), 0)
    p4 = adsk.core.Point3D.create(-buf1 * math.cos(rotth) - buf2 * math.sin(rotth), -buf1 * math.sin(rotth) + buf2 * math.cos(rotth), 0)
    sketch.sketchCurves.sketchArcs.addByCenterStartSweep(p0, p1, -(math.pi * 2.0 - a * 2.0))
    sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    sketch.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    sketch.sketchCurves.sketchLines.addByTwoPoints(p3, p4)
    # body
    prof = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(depth)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    extInput.setDistanceExtent(False, distance)
    extFeat = extrudes.add(extInput)
    endIndex = extFeat.timelineObject.index
    # timeline
    group = timelineGroups.add(startIndex, endIndex)
    group.name = 'Clean_vertical_hole'

def get_sketch_by_point(target_face, vector, point):
    # target data
    wx = point.worldGeometry.x
    wy = point.worldGeometry.y
    wz = point.worldGeometry.z
    # target data
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
    norm = adsk.core.Vector3D.create(nx, ny, nz)

    # get basic object
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root = design.rootComponent
    component = target_face.body.parentComponent
    extrudes = component.features.extrudeFeatures
    moveFeats = component.features.moveFeatures
    combines = component.features.combineFeatures
    planes = component.constructionPlanes
    # calcuration sketch plane
    sketchBase = component.sketches.add(root.xYConstructionPlane)
    p1 = adsk.core.Point3D.create(wx, wy, wz)
    p2 = adsk.core.Point3D.create(wx + vector.x, wy + vector.y, wz + vector.z)
    buf = adsk.core.Vector3D.create(p2.x-p1.x, p2.y-p1.y, p2.z-p1.z)
    mat = mutil.create_rotate_matrix(norm, -math.pi / 2.0)
    rot = mutil.calc_multiply(mat, buf)    
    p3 = adsk.core.Point3D.create(rot.x + p1.x, rot.y + p1.y, rot.z + p1.z)
    p1 = sketchBase.sketchPoints.add(p1)
    p2 = sketchBase.sketchPoints.add(p2)
    p3 = sketchBase.sketchPoints.add(p3)
    sketchBase.isVisible = False
    # add plane
    planeInput = planes.createInput()
    planeInput.setByThreePoints(p1, p2, p3)
    targetPlane = planes.add(planeInput)
    sketch = component.sketches.add(targetPlane)
    vecdir = sketch.yDirection
    th = mutil.get_angle(vector, vecdir)
    # rotate direction check
    mat1 = mutil.create_rotate_matrix(norm, th)
    buf1 = mutil.calc_multiply(mat1, vecdir)
    th1 = mutil.get_angle(vector, buf1)
    mat2 = mutil.create_rotate_matrix(norm, -th)
    buf2 = mutil.calc_multiply(mat2, vecdir)
    th2 = mutil.get_angle(vector, buf2)
    if th1 >= th2:
        return (sketch, th, sketchBase.timelineObject.index)
    else:
        return (sketch, -th, sketchBase.timelineObject.index)

def get_sketch_by_3dcircle(target_face, vector, edge):
    circle = adsk.core.Circle3D.cast(edge)
    # target data
    wx = circle.center.x
    wy = circle.center.y
    wz = circle.center.z
    nx = -circle.normal.x
    ny = -circle.normal.y
    nz = -circle.normal.z
    norm = adsk.core.Vector3D.create(nx, ny, nz)

    # get basic object
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    root = design.rootComponent
    component = target_face.body.parentComponent
    extrudes = component.features.extrudeFeatures
    moveFeats = component.features.moveFeatures
    combines = component.features.combineFeatures
    planes = component.constructionPlanes
    # calcuration sketch plane
    sketchBase = component.sketches.add(root.xYConstructionPlane)
    p1 = adsk.core.Point3D.create(wx, wy, wz)
    p2 = adsk.core.Point3D.create(wx + vector.x, wy + vector.y, wz + vector.z)
    buf = adsk.core.Vector3D.create(p2.x-p1.x, p2.y-p1.y, p2.z-p1.z)
    mat = mutil.create_rotate_matrix(norm, -math.pi / 2.0)
    rot = mutil.calc_multiply(mat, buf)    
    p3 = adsk.core.Point3D.create(rot.x + p1.x, rot.y + p1.y, rot.z + p1.z)
    p1 = sketchBase.sketchPoints.add(p1)
    p2 = sketchBase.sketchPoints.add(p2)
    p3 = sketchBase.sketchPoints.add(p3)
    sketchBase.isVisible = False
    # add plane
    planeInput = planes.createInput()
    planeInput.setByThreePoints(p1, p2, p3)
    targetPlane = planes.add(planeInput)
    sketch = component.sketches.add(targetPlane)
    vecdir = sketch.yDirection
    th = mutil.get_angle(vector, vecdir)
    # rotate direction check
    mat1 = mutil.create_rotate_matrix(norm, th)
    buf1 = mutil.calc_multiply(mat1, vecdir)
    th1 = mutil.get_angle(vector, buf1)
    mat2 = mutil.create_rotate_matrix(norm, -th)
    buf2 = mutil.calc_multiply(mat2, vecdir)
    th2 = mutil.get_angle(vector, buf2)
    if th1 >= th2:
        return (sketch, th, sketchBase.timelineObject.index)
    else:
        return (sketch, -th, sketchBase.timelineObject.index)