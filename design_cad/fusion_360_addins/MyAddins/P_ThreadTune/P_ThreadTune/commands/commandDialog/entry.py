# 4//9/2024    By: David Bunch
# Fine-Tune your Screw Thread Designs in Autodesk Fusion 360

import adsk.core, adsk.fusion, traceback
import math
import os
import csv
import time

from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
design = app.activeProduct
rootComp = design.rootComponent
ui = app.userInterface
preferences = app.preferences

ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = 'Bunch'
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'P_ThreadTune'
CMD_Description = 'Fine-Tune your Screw Thread Designs'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []
# Create a new occurrence (component).
def CreateNewComponent(Body_Name):
    allOccs = rootComp.occurrences
    transform = adsk.core.Matrix3D.create()
    occ1 = allOccs.addNewComponent(transform)
    subComp1 = occ1.component
    subComp1.name = Body_Name
    return(subComp1)
###############################################################################################
#############  Following routines below were generated from ChatGPT on 5/13/2024  #############
###############################################################################################
# The generated code had to be adjusted some to work within the framework of my program
def offset_point(px, py, ox, oy, distance):
#Offset a point (px, py) in the direction (ox, oy) by a specified distance.
    norm = math.sqrt(ox**2 + oy**2)
    return (px + distance * ox / norm, py + distance * oy / norm)
def det(a, b):
    return a[0] * b[1] - a[1] * b[0]
def line_intersection(l1, l2):
#Find the intersection of two lines given by points l1 and l2.
    xdiff = (l1[0].x - l1[1].x, l2[0].x - l2[1].x)
    ydiff = (l1[0].y - l1[1].y, l2[0].y - l2[1].y)
    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('Lines do not intersect')
    d = (det((l1[0].x, l1[0].y), (l1[1].x, l1[1].y)), det((l2[0].x, l2[0].y), (l2[1].x, l2[1].y)))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return adsk.core.Point3D.create(x, y, 0)
# Offsetting direction is perpendicular to the line segment direction
def perpendicular_vector(px, py):
    return -py, px
def Real_offset(pts):
# Offset points for each line segment
    P1 = pts[0]
    P2 = pts[1]
    P3 = pts[2]
    P4 = pts[3]
    P5 = pts[4]
    P6 = pts[5]
    offset_distance = (abs(float(_MF_Gap.text)) * 0.1) * 1 
    points = [
        (P1.x, P1.y), 
        (P2.x, P2.y), 
        (P3.x, P3.y), 
        (P4.x, P4.y), 
        (P5.x, P5.y), 
        (P6.x, P6.y)
    ]
# Offset points for each line segment
    offsets = []
    for i in range(len(points) - 1):
        p_start = points[i]
        p_end = points[i + 1]
        direction = perpendicular_vector(p_end[0] - p_start[0], p_end[1] - p_start[1])
        offset_start = offset_point(p_start[0], p_start[1], direction[0], direction[1], offset_distance)
        offset_end = offset_point(p_end[0], p_end[1], direction[0], direction[1], offset_distance)
        offsets.append((
            adsk.core.Point3D.create(offset_start[0], offset_start[1], 0),
            adsk.core.Point3D.create(offset_end[0], offset_end[1], 0)
        ))
# Find intersections of consecutive offset lines
    vertex_points = []
    for i in range(len(offsets) - 1):
        vertex_point = line_intersection(offsets[i], offsets[i + 1])
        vertex_points.append(vertex_point)
    return vertex_points
##########################################################################
def draw_regular_polygon(sketch, num_sides, rad):
# Calculate the coordinates of the polygon's vertices
    angle_offset = math.pi / num_sides
    vertices = []
    for i in range(num_sides):
        angle = angle_offset + i * (2 * math.pi / num_sides)
        x = rad * math.cos(angle)
        y = rad * math.sin(angle)
        vertices.append(adsk.core.Point3D.create(x, y, 0))
# Draw lines connecting the vertices
    lines = []
    for i in range(num_sides):
        start_point = vertices[i]
        end_point = vertices[(i + 1) % num_sides]
        lines.append(sketch.sketchCurves.sketchLines.addByTwoPoints(start_point, end_point))
    return lines
#########################################################################################
##########  Following routines above were generated from ChatGPT on 5/13/2024  ##########
#########################################################################################
def create_offset_plane_from_xy(subComp1, construction_plane, offset_distance):
# Get the construction planes collection.
    planes = subComp1.constructionPlanes
# Get the XY construction plane.
    xy_plane = subComp1.xYConstructionPlane
# Create an offset plane from the XY construction plane.
    offset_plane_input = planes.createInput()
    offset_plane_input.setByOffset(xy_plane, adsk.core.ValueInput.createByReal(offset_distance))
    offset_plane = planes.add(offset_plane_input)
    return offset_plane
##########################################################################
def create_circle_sketch_on_plane(subComp1, plane, radius):
# Get the sketches collection of the root component.
    sketches = subComp1.sketches
# Create a sketch on the given plane.
    sketch = sketches.add(plane)
# Draw a circle at the origin with the given radius.
    center_point = adsk.core.Point3D.create(0, 0, 0)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, radius)
    return sketch
##########################################################################
def DrawBoltHead(subComp1, BoltFlat_Dia, num_sides, BoltHd_Ht):
    Flat_OD = BoltFlat_Dia * .1         # Diameter between Flats
    Flat_Rad = Flat_OD / 2              # Rad of Flat Diamter
    Ang1 = 360.0 / (num_sides * 2)      # Amgle between a Vertex & center of a Flat
    PI1 = math.pi                       # Value of pi
    R_Ang1 = Ang1 * PI1 / 180.0         # Angle in radians
    Rad = Flat_Rad / math.cos(R_Ang1)   # Radius to a Vertex

    sketches = subComp1.sketches
    xyPlane = subComp1.xYConstructionPlane
    sketch_Head = sketches.add(xyPlane)
    sketch_Head.name = "sketch_Head"
# Draw the regular polygon
    draw_regular_polygon(sketch_Head, num_sides, Rad)
# Get the profile defined by the Polygon.
    profPoly = sketch_Head.profiles.item(0)
    Ht2 = adsk.core.ValueInput.createByReal(-BoltHd_Ht * .1)
    extrudes = subComp1.features.extrudeFeatures
    extrudes.addSimple(profPoly, Ht2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
##########################################################################
def DrawNut(subComp1, NutFlat_Dia, num_sides, NutHd_Ht, Pitch):
    Flat_OD = NutFlat_Dia * .1         # Diameter between Flats
    Flat_Rad = Flat_OD / 2              # Rad of Flat Diamter
    Ang1 = 360.0 / (num_sides * 2)      # Amgle between a Vertex & center of a Flat
    PI1 = math.pi                       # Value of pi
    R_Ang1 = Ang1 * PI1 / 180.0         # Angle in radians
    Rad = Flat_Rad / math.cos(R_Ang1)   # Radius to a Vertex
    sketches = subComp1.sketches
# Get the XY construction plane.
    xy_plane = create_offset_plane_from_xy
    offset_plane = create_offset_plane_from_xy(subComp1, xy_plane, float(Pitch * .1))
    sketch_Nut = sketches.add(offset_plane)
    sketch_Nut.name = "sketch_Nut"
# Draw the regular polygon
    draw_regular_polygon(sketch_Nut, num_sides, Rad)
# Get the profile defined by the Polygon.
    profPoly = sketch_Nut.profiles.item(0)
    Ht2 = adsk.core.ValueInput.createByReal(NutHd_Ht * .1)
    extrudes = subComp1.features.extrudeFeatures
    extrudes.addSimple(profPoly, Ht2, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
##########################################################################
def ChamferTopThreads(subComp1, Rad, Ht, Ch_Wid):
    Rad1 = Rad * .1
    Ht1 = (Ht + .01) * .1
    Ch_Wid = abs(Ch_Wid)
    CW = Ch_Wid * .1
    X0 = Rad1 - CW
    Y2 = Ht1 - CW
    Rd1 = Rad1 + 0.001
    P10 = adsk.core.Point3D.create(0, -Ht1, 0)
    P1 = adsk.core.Point3D.create(X0, -Ht1, 0)
    P2 = adsk.core.Point3D.create(Rd1, -Y2, 0)
    P3 = adsk.core.Point3D.create(Rd1, -Ht1, 0)
    sketches = subComp1.sketches
    sketch_Chamfer = sketches.add(subComp1.xZConstructionPlane)
    sketch_Chamfer.name = "Chamfer_Thread"
    sketch_Rev = sketch_Chamfer.sketchCurves.sketchLines
# Draw a line to use as the axis of revolution.
    axisLine = sketch_Rev.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0),P10)
    sketch_Rev.addByTwoPoints(P1,P2)
    sketch_Rev.addByTwoPoints(P2,P3)
    sketch_Rev.addByTwoPoints(P3,P1)
# Get the profile defined by the Chamfer.
    prof = sketch_Chamfer.profiles.item(0)
# Create an revolution input to be able to define the input needed for a revolution
# while specifying the profile and that a new component is to be created
    revolves = subComp1.features.revolveFeatures
    revInput = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.CutFeatureOperation)
# Define that the extent is an angle of pi to get half of a torus.
    angle = adsk.core.ValueInput.createByReal(math.pi * 2.0)
    revInput.setAngleExtent(False, angle)
# Create the extrusion.
    revolves.add(revInput)
##########################################################################
def ChamferNut(subComp1, OD1, Pit, PitHlx, Ht, Ch_Wid, iTY_Char):
    if iTY_Char < 4:
        ChamferTopThreads(subComp1, OD1 / 2, Ht,Ch_Wid)
    else:
        Ch_Wid = abs(Ch_Wid)
        Pit1 = Pit * .1
        Ht1 = (Ht + .01) * .1
        Ht1 = (Ht + .01) * .1 + Pit1
        Pt1 = Pit1 - .001
        YHt = (Ht1 - Pt1) / 2.0
        CW = Ch_Wid * .1                # Convert to mm
        PitHlx1 = PitHlx * .1
        pts = calcPts(OD1, Pit, PitHlx1)          # Run this to get R_Min
        R_Min1 = pts[7]
        Rd1 = R_Min1 - 0.001
        X0 = Rd1 + CW
        X1 = X0 - YHt
        Y1 = Pt1 + YHt
        P11 = adsk.core.Point3D.create(0, -Pt1, 0)
        P12 = adsk.core.Point3D.create(X0, -Pt1, 0)
        P13 = adsk.core.Point3D.create(X1, -Y1, 0)
        P14 = adsk.core.Point3D.create(X0, -Ht1, 0)
        P15 = adsk.core.Point3D.create(0, -Ht1, 0)

        sketches = subComp1.sketches
        sketch_Chamfer = sketches.add(subComp1.xZConstructionPlane)
        sketch_Chamfer.name = "Chamfer_Thread"
        sketch_Rev = sketch_Chamfer.sketchCurves.sketchLines
# Draw a line to use as the axis of revolution.
        axisLine = sketch_Rev.addByTwoPoints(P11,P15)
        sketch_Rev.addByTwoPoints(P11,P12)
# We crossed the centerline with chamfer profile, so adjust to have only 1 profile
        if X1 < 0:
            P16 = adsk.core.Point3D.create(.01, -Pt1, 0)        # Bottom Vertical Intersection Line
            P17 = adsk.core.Point3D.create(.01, -Ht1, 0)        # Top Vertical Intersection Line

            P50 = findIntersection(P16, P17, P12, P13)          # Intersection of bottom 45 degree line
            P51 = findIntersection(P16, P17, P13, P14)          # Intersection of top 45 degreee line
            sketch_Rev.addByTwoPoints(P12,P50)
            sketch_Rev.addByTwoPoints(P50,P51)
            sketch_Rev.addByTwoPoints(P51,P14)
            sketch_Rev.addByTwoPoints(P14,P15)
        else:
            sketch_Rev.addByTwoPoints(P12,P13)
            sketch_Rev.addByTwoPoints(P13,P14)
            sketch_Rev.addByTwoPoints(P14,P15)
# Get the profile defined by the Chamfer.
        prof = sketch_Chamfer.profiles.item(0)
        profiles = adsk.core.ObjectCollection.create()
        profiles.add(prof)
# Create an revolution input to be able to define the input needed for a revolution
        revolves = subComp1.features.revolveFeatures
        revInput = revolves.createInput(profiles, axisLine, adsk.fusion.FeatureOperations.CutFeatureOperation)
# Define that the extent is an angle of pi to get half of a torus.
        angle = adsk.core.ValueInput.createByReal(math.pi * 2.0)
        revInput.setAngleExtent(False, angle)
# Create the extrusion.
        revolves.add(revInput)
##########################################################################
def count_sketch_profiles(sketch):
    profile_count = 0
    for sketch_entity in sketch.sketchEntities:
        if sketch_entity.objectType == adsk.fusion.SketchProfiles.classType():
            profile_count += 1
    return profile_count
##########################################################################
def DrawCylinder(subComp1, sketch_Helix, Rad, R_Min, Ht1, Pitch, PitHlx, iflag, iTY_Char):
    sketches = subComp1.sketches
    xyPlane = subComp1.xYConstructionPlane
    sketch_Cyl = sketches.add(xyPlane)
    sketch_Cyl.name = "Sketch_Cylinder"
# Draw a circle.
    circles = sketch_Helix.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), R_Min)
    circles1 = sketch_Cyl.sketchCurves.sketchCircles
    circles1.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), (Rad * .1) + .01)
# Get the profile defined by the circle.
    profCir = sketch_Helix.profiles.item(0)
    profCir1 = sketch_Cyl.profiles.item(0)
    Ht2 = adsk.core.ValueInput.createByReal(Ht1)
    extrudes = subComp1.features.extrudeFeatures
    try:
        extrudes.addSimple(profCir, Ht2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    except:
        extrudes.addSimple(profCir, Ht2, adsk.fusion.FeatureOperations.CutFeatureOperation)           # sometimes Joining does not work, so if it fails try cutting 1st
        extrudes.addSimple(profCir, Ht2, adsk.fusion.FeatureOperations.JoinFeatureOperation)          # Then join it & that worked for the problem I had with it
# Cut the threads that are below origin
    Ht3 = adsk.core.ValueInput.createByReal(-((YB_B * 2) + (PitHlx * 2 * .1)))
    try:
        extrudes.addSimple(profCir1, Ht3, adsk.fusion.FeatureOperations.CutFeatureOperation)
    except:
        msg = 'Last Cut Feature below origin in DrawCylinder failed for some reason, but might not be a problem'
        ui.messageBox(msg,"Warning", adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)
# Get the XY construction plane.
    xy_plane = create_offset_plane_from_xy
# Create the offset plane.
    Ht4 = float(Ht1)
    Ht5 = adsk.core.ValueInput.createByReal(YB_T * 2 + PitHlx * 2 * .1)
    offset_plane = create_offset_plane_from_xy(subComp1, xy_plane,Ht4)
# Create sketch on the offset plane and draw a circle.
    sketchTop = create_circle_sketch_on_plane(subComp1, offset_plane, (Rad * .1) + .01)
    profCir2 = sketchTop.profiles.item(0)
    try:
        extrudes.addSimple(profCir2, Ht5, adsk.fusion.FeatureOperations.CutFeatureOperation)
    except:
        msg = 'Last Cut Feature of DrawCylinder failed for some reason, but might not be a problem'
        ui.messageBox(msg,"Warning", adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)
# For some reaason this sketch stays turned on when drawing the cylinder for the Nut threads
    if sketch_Cyl.isVisible:
        sketch_Cyl.isVisible = False
##########################################################################
def DrawHelix(subComp1, sketch_Helix, C_Min, Rad, Pitch, Ht, Ht1, sPts, G_Rail, RL_thread, prof, iflag):
    global Vert_Line
    P10 = adsk.core.Point3D.create(0,0,Ht1)
    rev = int(Ht / Pitch) + 1               # Number of revolutions, add one to it so we don't do a partial revolution
    Pitch2 = Pitch * 0.1
    Pitch1 = round(Pitch2, 6)
# Create an object collection for the points.
    sketchSplines = sketch_Helix.sketchCurves.sketchFittedSplines
    sketchCenter = sketch_Helix.sketchCurves.sketchLines    # used for Centerline Guide Rail, does not work as well as Helix
    P0 = adsk.core.Point3D.create(0,0,0)
    Vert_Line = sketchCenter.addByTwoPoints(P0,P10)         # Draw Center Vertical for Guide Rail with Sweeep
    Z0 = 0.0
    Rad1 = Rad * .1
    ang1 = 360.0 / sPts                             # Increment angle in degrees between horizontal spline points
    ang_R = ang1 * math.pi / 180                    # Increment angle in radians between horizontal spline points
    if RL_thread == 'L':
        ang_R = ang_R * -1                          # Left hand threads increment in the negative direction
    Z_inc = Pitch1 / sPts                           # Z increment amount between spline points
    sPts_Total = sPts                               # Number of spline points for 1 revolution of Helix
    if G_Rail == 'L':
        sPts_Total = sPts * rev                     # Number of spline points for Continuous Long Helix
    Icount = 0                                      # Initalize Loop counter
    ang = 0                                         # Set beginning angle of Helix spline poing
    points = adsk.core.ObjectCollection.create()    # Create the points collection for the inner Helix Path
    points1 = adsk.core.ObjectCollection.create()   # Create the points collection for the outer Helix Guide Rail
    pts = calcPts(Rad * 2, Pitch, Pitch1)           # Run this to get R_Min
    R_Min1 = pts[7]
    while (Icount <= sPts_Total):
        x = R_Min1 * math.cos(ang)                  # Helix x, y points along inside Radius minus .1mm to connect multiple threads
        y = R_Min1 * math.sin(ang)
        z = Z0
        Z0 = Z0 + Z_inc                             # Increment the Z to get to next spline Z coordinate
        if G_Rail != 'C':
            x1 = Rad1 * math.cos(ang)               # Helix x, y points along outside radius of thread
            y1 = Rad1 * math.sin(ang)
            points1.add(adsk.core.Point3D.create(x1, y1, z))     # Need 2nd spline for guide rail
        points.add(adsk.core.Point3D.create(x, y, z))
        ang = ang + ang_R                           # Increment angle for next coordiante in loop
        Icount = Icount + 1                         # increment loop counter
    spline = sketchSplines.add(points)              # Create the inner spline helix from points
    if G_Rail != 'C':
        spline1 = sketchSplines.add(points1)        # Create the outer spline helix from points
        guide = subComp1.features.createPath(spline1)        
    path = subComp1.features.createPath(spline)
    guideLine = subComp1.features.createPath(Vert_Line)     # Guide for Centerline in case user wants that option
# Create a sweep input
    sweeps = subComp1.features.sweepFeatures
    sweepInput = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    if G_Rail == 'C':
        sweepInput.guideRail = guideLine
    else:
        sweepInput.guideRail = guide            # Default guide rail is the outer Helix
    sweepInput.profileScaling = adsk.fusion.SweepProfileScalingOptions.SweepProfileScaleOption
# Create the sweep.
    sweeper = sweeps.add(sweepInput)              # This seems to be the slowest part of the code
    if iflag < 1:
        body1 = sweeper.bodies.item(0)
        body1.name = Body_Name                  # rename body to most of input parameters from main routine
##########################################################################
def ReCalcHelixPitch(idx):
    idx_array = [1, 2, 4]                           # 1 start, 2 start, 4 start
    x = idx_array[idx]
    pit = _pitch.text         # ReCalcHelix does not access global variable pitch for some reason, so get it from dialog box
    _pitHelix.text = repr(float(pit) * x)    # Set the pitch of the helix
def CalcThread(iTest):
    Eng_ID = dropdownInputEM.selectedItem.index         # 0 = English, 1 = Metric
    if Eng_ID == 1:
        diameter = _diameter.text
        pitch = _pitch.text
        PitHlx = float(pitHelix)
    else:
        Ediameter = _Ediameter.text
        diameter = repr(float(Ediameter) * 25.4)             # Convert all English values to mm before processing the data
        Epitch = _Epitch.text
        pitch = repr((1.0 / float(Epitch)) * 25.4)
        EpitHelix = _EpitHelix.text
        PitHlx = (1.0 / float(EpitHelix)) * 25.4
    OD = float(diameter)
    PitHlx1 = PitHlx * .1                           # Convert helix pitch to mm
    pts = calcPts(OD, float(pitch), PitHlx1)           # Calculates P1, P2, P3, P4 used here
    P1 = pts[1]
    P2 = pts[2]
    P3 = pts[3]
    P4 = pts[4]
    X_Dist = (abs(P2.x) - abs(P1.x)) * 10.0
    if AngT < 0 or AngB < 0:
        Y_Dist = abs((abs(P3.y) + abs(P2.y)) * 10.0)
    else:
        Y_Dist = abs((abs(P4.y) + abs(P1.y)) * 10.0)
    if Eng_ID == 1:
        Thread_Wid = "{:.4f}".format(X_Dist)
        Thread_Ht = "{:.4f}".format(Y_Dist)
 # Only change Cham_Wid initially when iTest == 0
 # otherwise the update routine that calls this will change it & user would never be able to adjust Cham_Wid within dialog box
        if iTest == 0:
            F_Cham_Wid = (X_Dist * 1.9)
            Cham_Wid = "{:.4f}".format(F_Cham_Wid)
            _Cham_Wid.text = Cham_Wid
        _Thread_Wid.text = Thread_Wid
        _Thread_Ht.text = Thread_Ht
    else:
        Thread_EWid = "{:.4f}".format(X_Dist / 25.4)
        Thread_EHt = "{:.4f}".format(Y_Dist / 25.4)
        if iTest == 0:
            F_Cham_EWid = ((X_Dist / 25.4) * 1.9)
            Cham_EWid = "{:.4f}".format(F_Cham_EWid)
            _Cham_EWid.text = Cham_EWid
        _Thread_EWid.text = Thread_EWid
        _Thread_EHt.text = Thread_EHt
##########################################################################
def calcPts(OD, Pitch, PitHlx1):
    global YB_B                                 # These 2 are used for cutting bottom & top of threads flush
    global YB_T
    global AngT, AngB
    PI1 = math.pi
# We want to use the absolute value of largest angle to use with formulas to get R_Min
    angleTop = _angleTop.text
    angleBot = _angleBot.text
    AngT = float(angleTop)
    AngB = float(angleBot)
    abs_angT = abs(AngT)
    abs_angB = abs(AngB)
    ang = abs_angB
    if abs_angT < abs_angB:
        ang = abs_angT
    if ang == 0.0:
        ang = 30.0
    if AngT < 0 and AngB < 0:
        if abs_angT > abs_angB:
            ang = AngT
        else:
            ang = AngB
    T_Ang = math.tan(float(AngT) * PI1/float(180.0))
    B_Ang = math.tan(float(AngB) * PI1/float(180.0))
    C_Ang = math.tan(float(ang) * PI1/float(180.0))
    Rad = OD / 2.0
    H_Thread = (1 / C_Ang) * (Pitch / 2)
    H8 = H_Thread / 8
    H_5H8 = (5 * H_Thread) / 8
    H3 = ((H_5H8 + H8) * C_Ang) * 0.1
    D_Min = (OD - (2 * abs(H_5H8))) * 0.1
    R_Min = D_Min / 2
    R_Min1 = D_Min / 2 - .01    # need just a little more inward to get one profile for multiple threads
# To be less confusing, make sure we are dealing with positive numbers
    YB_B = abs((H_5H8 + H8) * B_Ang * .1)       # Biggest Length closest to center
    YS_B = abs(H8 * B_Ang * .1)
    YB_T = abs((H_5H8 + H8) * T_Ang * .1)       # Smallest Length on Outside Diameter
    YS_T = abs(H8 * T_Ang * .1)
# Center of everthing is at Origin 0,0,0
    X0 = R_Min1
    X1 = R_Min
    X2 = Rad * 0.1
    X3 = X2
    X4 = X1
# For some reason Negative numbers are above X-axis & Positive numbers are below X-axis
    if AngB > 0:
        P1 = adsk.core.Point3D.create(X1, YB_B, 0)
        P2 = adsk.core.Point3D.create(X2, YS_B, 0)
    elif AngB == 0:
        P1 = adsk.core.Point3D.create(X1, H3, 0)
        P2 = adsk.core.Point3D.create(X2, H3, 0)
    elif AngB < 0:
        P1 = adsk.core.Point3D.create(X1, YS_B, 0)
        P2 = adsk.core.Point3D.create(X2, YB_B, 0)
# Points for Top Angle
    if AngT > 0:
        P3 = adsk.core.Point3D.create(X3, -YS_T, 0)
        P4 = adsk.core.Point3D.create(X4, -YB_T, 0)
    elif AngT == 0:
        P3 = adsk.core.Point3D.create(X3, -H3, 0)
        P4 = adsk.core.Point3D.create(X4,-H3, 0)
    elif AngT < 0:
        P3 = adsk.core.Point3D.create(X3, -YB_T, 0)
        P4 = adsk.core.Point3D.create(X4, -YS_T, 0)
# Special case of Negative top angle & Positive bottom angle
    if AngT < 0 and AngB > 0:
        P1 = adsk.core.Point3D.create(X1, YB_B, 0)
        P2 = adsk.core.Point3D.create(X2, YS_B, 0)
        P3 = adsk.core.Point3D.create(X3, -YB_T, 0)
        P4 = adsk.core.Point3D.create(X4, -YS_T, 0)
# Special case of Positive top angle & Negative bottom angle
    if AngT > 0 and AngB < 0:
        P1 = adsk.core.Point3D.create(X1, YS_B, 0)
        P2 = adsk.core.Point3D.create(X2, YB_B, 0)
        P3 = adsk.core.Point3D.create(X3, -YS_T, 0)
        P4 = adsk.core.Point3D.create(X4, -YB_T, 0)
    Y0 = P1.y
    Y5 = Y0 - PitHlx1
    P00 = adsk.core.Point3D.create(X0, Y0, 0)
    P5 = adsk.core.Point3D.create(X1, Y5, 0)
    points = [P00, P1, P2, P3, P4, P5, X0, R_Min]
    return(points)
##########################################################################
    # global CoilType         # Type of Coil to Draw
# 1 Revolution and Height (also has optional angle)
# 2 Revolution and Pitch (also has optional angle)
# 3 Height and Pitch (also has optional angle)
# 4 Spiral
    # global Cdiameter        # Diameter of Coil
    # global Crevs            # Number of Coil Revolutions
    # global Cheight          # Height of Coil
    # global Cpitch           # Pitch of Coil
    # global Cangle           # Coil Angle (0 = no angle)
    # global CsplinePts       # Number of Spline points per revolution for Coil
    # global GRC_Char         # Coil GuideRail Type LongHelix or Pattern (Not Used for Now)
    #                         # Pattern will not work with Spiral or angle used with other coil types
    # global Cdia_Sect        # Diameter of Circle or Polygon Profile for Coil
    # global CpolySides       # Number of Sides for Polygon Profile
    # global Crect_Wid        # Width of Rectangle Profile
    # global Crect_Ht         # Height of Rectangle Profile
    # global CStarOut_Rad     # Outside Radius of Star Profile
    # global CStarIn_Rad      # Inside Radius of Star Profile
    # global CStar_Num        # Number of Star Points
    # global CSec_Type        # Profile Section type, 1 (Circle), 2 (Polygon), 3 (Ellipse), 4 (Rectangle) or 5 (Star)
    # global Cposition        # 1st character is 1 (inside), 2 (On Center) or 3 (Outside)
    # global CPosRect         # Rectangle Profile vertical position 1 = Top, 2 = Middle, 3 = Bottom
def DrawCoil(subComp1, CoilType, Cdiameter, CSec_Type, CpolySides, CellipseX, CellipseY, Cposition, CPosRect, Crect_Wid, Crect_Ht, CStarOut_Rad, CStarIn_Rad, CStar_Num, Cpitch, Crevs, Cheight, sPts, GRC_Char, RL_thread, Cangle, CvertPos):
    F_OD = float(Cdiameter)     # Starting Diameter of coil or spiral
    F_Rad = F_OD / 2.0
    F_Rad1 = F_Rad * .1
    I_revs = int(Crevs)         # Number of revolutions if this option used
    Ht = float(Cheight)         # Height of Coil if this option used
    F_angle = float(Cangle)
    F_ID = float(Cdia_Sect)
    F_ID_Rad = F_ID / 2
    F_ID_Rad1 = F_ID_Rad * .1
    numSides = int(CpolySides)
    I_num_points = int(CStar_Num)
    F_pitch = float(Cpitch)
    R_Max1 = (F_Rad + F_ID_Rad) * .1
    #ui.messageBox(f'CoilType = {CoilType}\n CellipseX = {CellipseX}\nCellipseY = {CellipseY}')
# Create a new 3D sketch.
    sketches = subComp1.sketches
    sketch_Profile = sketches.add(subComp1.xZConstructionPlane)
    sketch_Profile.name = "Coil_Profile"
    F_Pos = F_Rad1
    S_Type = 'Circle_'
    S_Pos = 'CtrPos_'
# Inside position moves the section inward & outside position moves the section outward, backwards from what I originally thought
    if Cposition == '1':
        S_Pos = 'InPos_'
        F_Pos = F_Rad1 - F_ID_Rad1
    elif Cposition == '3':
        S_Pos = 'OutPos_'
        F_Pos = F_Rad1 + F_ID_Rad1
# Profile Section type, 1 (Circle), 2 (Polygon), 3 (Ellipse), 4 (Rectangle) or 5 (Star)
    if CSec_Type == '1':
        DrawCircle(sketch_Profile, F_Pos, F_ID_Rad1)
    if CSec_Type == '2':
        S_Type = "Poly_" + CpolySides + "_Sides_"
# Only run through this code if we are not locating the polygon on the center point
        if Cposition != '2':
# 1st pass through DrawPolygon we calculate the Left & Right intersection points of X-axis & polygon
            X_Pts = DrawPolygon(sketch_Profile, F_Rad1, numSides, F_ID_Rad1, CvertPos, 0) # Returns 2 intersection points of polygon with X-axis
            if X_Pts:
                X_Min = X_Pts[0]
                R_Max1 = X_Pts[1]
                X_LtDist = F_Rad1 - X_Min
                X_RtDist = R_Max1 - F_Rad1
    # ReCompute the Left side & Right side offset for polygon location
                if Cposition == '1':
                    F_Pos = F_Rad1 - X_RtDist
                elif Cposition == '3':
                    F_Pos = F_Rad1 + X_LtDist
        X_Pts = DrawPolygon(sketch_Profile, F_Pos, numSides, F_ID_Rad1, CvertPos, 1)
        if X_Pts:
            F_Rad1 = X_Pts[0]           # This is to keep R_Max1 & F_Rad1 being the same number when Cposition = '3'
            R_Max1 = X_Pts[1]
    elif CSec_Type == '3':
        S_Type = 'Ellipse_'
        X_Dist1 = float(CellipseX) * .1
        Y_Dist1 = float(CellipseY) * .1
        F_Pos = F_Rad1
        if Cposition == '1':
            F_Pos = F_Rad1 - (X_Dist1 / 2)
        elif Cposition == '3':
            F_Pos = F_Rad1 + (X_Dist1 / 2)
        DrawEllipse(sketch_Profile, F_Pos, X_Dist1, Y_Dist1)
    elif CSec_Type == '4':
        S_Type = "Rect_" + Crect_Wid + "mm_Wid_" + Crect_Ht + "mm_Ht_"
        X_Pts = DrawRectangle(sketch_Profile, F_Rad1, Crect_Wid, Crect_Ht, Cposition, CPosRect)
        F_Rad1 = X_Pts[0]
        R_Max1 = X_Pts[1]
    elif CSec_Type == '5':
        S_Type = "Star_"
        F_OutRad = float(CStarOut_Rad) * .1
        F_InRad = float(CStarIn_Rad) * .1
        F_Pos = F_Rad1
        if Cposition == '1':
            F_Pos = F_Rad1 - F_InRad
        elif Cposition == '3':
            F_Pos = F_Rad1 + F_InRad
        DrawStar(sketch_Profile, F_Pos, F_OutRad, F_InRad, I_num_points, CvertPos)
        R_Max1 = F_Rad1 + F_InRad
    prof = sketch_Profile.profiles.item(0)
# Get the profiles in the sketch
    xyPlane = subComp1.xYConstructionPlane
    sketch_Helix = sketches.add(xyPlane)
    sketch_Helix.name = "Sketch_Helix"
    if CoilType == '4':
        subComp1.name = "Spiral_" + S_Pos + S_Type + Cdiameter
        DrawSpiral(subComp1, sketch_Helix, F_Rad1, F_pitch, I_revs, sPts, RL_thread, prof)
    else:
        subComp1.name = "Coil_" + S_Pos + S_Type + Cdiameter
        DrawAngledCoil(subComp1, sketch_Helix, R_Max1, F_Rad1, F_pitch, I_revs, Ht, F_angle, sPts, prof, CoilType)
    b_name = subComp1.name
    bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
    numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used, should be 3
    if numBodies > 0:
        target_body = bsubComp1_bodies.item(0)    # This should be the Nut just drawn
        target_body.name = b_name
##########################################################################
# Revolution and Height (also has optional angle)
# (Done) Revolution and Pitch (also has optional angle)
# Height and Pitch (also has optional angle)
# (Done) Spiral
##########################################################################
def DrawSpiral(subComp1, sketch_Helix, Rad1, pitch, revolutions, num_points_per_revolution, RL_thread, prof):
    pitch1 = pitch * .1
    points = adsk.core.ObjectCollection.create()
# Determine the direction of rotation
    if RL_thread == 'L':
        direction = -1
    else:
        direction = 1
# Create an object collection for the points.
    sketchSplines = sketch_Helix.sketchCurves.sketchFittedSplines
# Calculate points for the spiral
    for i in range(num_points_per_revolution * revolutions + 1):
        t = direction * i / num_points_per_revolution * 2 * math.pi
        r = Rad1 + (pitch1 * abs(t)) / (2 * math.pi)
        x = r * math.cos(t)
        y = r * math.sin(t)
        z = 0
        points.add(adsk.core.Point3D.create(x, y, z))
# Create the spline
    spline = sketchSplines.add(points)              # Create the inner spline helix from points 
    path = subComp1.features.createPath(spline)
# Create the sweep feature
    sweeps = subComp1.features.sweepFeatures
    sweep_input = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweeps.add(sweep_input)
##########################################################################
# 1 (done) Revolution and Height (also has optional angle)
# 2 Revolution and Pitch (also has optional angle)
# 3 (done) Height and Pitch (also has optional angle)
# 4 (done) Spiral
#   DrawAngledCoil(subComp1, sketch_Helix, F_Rad + F_ID_Rad, F_Rad, F_pitch, I_revs, Ht, F_angle, sPts, prof, CoilType)
#DrawAngledCoil(subComp1, sketch_Helix, R_Max, F_Rad, F_pitch, I_revs, Ht, F_angle, sPts, prof, CoilType) F_Rad = Path Radius, R_Max = Guide Rail Radius
def DrawAngledCoil(subComp1, sketch_Helix, R_Max1, F_Rad1, F_pitch, I_revs, Ht, F_angle, sPts, prof, CoilType):
# Convert angle from degrees to radians
    angle = math.radians(F_angle)
# Convert diameter and pitch from mm to cm
    rad0 = F_Rad1           # F_Rad = Path Radius
    rad1 = R_Max1           # R_Max = Guide Rail Radius
    pitch = F_pitch * .1
    Ht1 = Ht * .1
    if CoilType == '1':
        pitch = Ht1 / I_revs
    elif CoilType == '2':
        Ht1 = I_revs * pitch
# Calculate the radius and total points
    total_points = sPts * I_revs
# Create an object collection for the points.
    sketchSplines = sketch_Helix.sketchCurves.sketchFittedSplines
# Calculate the points for the coil
    points = adsk.core.ObjectCollection.create()
    points1 = adsk.core.ObjectCollection.create()
    for i in range(total_points + 1):
        t = i / sPts * 2 * math.pi  # angle in radians
        r = rad0 + (pitch * i / sPts) * math.tan(angle)
        r1 = rad1 + (pitch * i / sPts) * math.tan(angle)
        x = r * math.cos(t)
        y = r * math.sin(t)
        x1 = r1 * math.cos(t)
        y1 = r1 * math.sin(t)
        z = (pitch / (2 * math.pi)) * t  # linear z increase with t
        points.add(adsk.core.Point3D.create(x, y, z))       # for Path
        points1.add(adsk.core.Point3D.create(x1, y1, z))    # for GuideRail
# Create the spline
    spline = sketchSplines.add(points)              # Create the inner spline helix from points
    spline1 = sketchSplines.add(points1)
    guide = subComp1.features.createPath(spline1)
    path = subComp1.features.createPath(spline)
# Create the sweep feature
    sweeps = subComp1.features.sweepFeatures
    sweep_input = sweeps.createInput(prof, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweep_input.guideRail = guide            # Default guide rail is the outer Helix
    sweep_input.profileScaling = adsk.fusion.SweepProfileScalingOptions.SweepProfileScaleOption
    sweeps.add(sweep_input)
##########################################################################
def DrawCircle(sketch_Profile, F_Pos, F_ID_Rad1):
    center_point = adsk.core.Point3D.create(F_Pos, 0, 0)
    sketch_Profile.sketchCurves.sketchCircles.addByCenterRadius(center_point, F_ID_Rad1)
##########################################################################
def SetStartAngle(CvertPos):
    initialAngle = 0 # 0 degrees Right vertex
    if CvertPos == '2':
        initialAngle = - math.pi / 2 # -90 degrees Top vertex
    elif CvertPos == '3':
        initialAngle = math.pi # 180 degrees Left vertex
    elif CvertPos == '4':
        initialAngle = math.pi / 2 # 90 degreesBottom vertex
    elif CvertPos == '5':
        initialAngle = math.pi / 8 # 22.5 degrees for 8 sided
    elif CvertPos == '6':
        initialAngle = math.pi / 4 # 45.0 degrees for 12 sided
    return (initialAngle)
##########################################################################
def DrawPolygon(sketch_Profile, F_Pos, numSides, radius, CvertPos, iflag):
    centerX = F_Pos             # Center X coordinate of Polygon
    centerY = 0
# Define the initial angle to adjust the position of the vertices
    initialAngle = SetStartAngle(CvertPos)
    angle = 2 * math.pi / numSides
    points = []
    for i in range(numSides):
        x = centerX + radius * math.cos(i * angle + initialAngle)
        y = centerY + radius * math.sin(i * angle + initialAngle)
        points.append(adsk.core.Point3D.create(x, y, 0)) # Center point is (x, y) on the XY plane, z is constant
# Create the lines between the points only on 2nd pass through this routine
    if iflag == 1:
        lines = sketch_Profile.sketchCurves.sketchLines
        for i in range(numSides):
            lines.addByTwoPoints(points[i], points[(i + 1) % numSides])
# Find the intersection points with the X-axis (y=0)
    X_Pts = []
    for i in range(numSides):
        p1 = points[i]
        p2 = points[(i + 1) % numSides]
# Calculate intersection with the X-axis (y=0)
        if (p1.y >= 0 > p2.y) or (p1.y <= 0 < p2.y):
            t = p1.y / (p1.y - p2.y)
            xIntersect = p1.x + t * (p2.x - p1.x)
            X_Pts.append(xIntersect)
    # Display the intersection points
    if len(X_Pts) >= 2:
        X10 = X_Pts[0]
        X20 = X_Pts[1]
        if X10 > X20:
            X_Min = X20
            X_Max = X10
        else:
            X_Min = X10
            X_Max = X20
        X_MinMax = [X_Min, X_Max]
        return (X_MinMax)
    else:
        return (False)
##########################################################################
def DrawEllipse(sketch_Profile, F_Pos, Major_X, Minor_Y):
# Define the ellipse parameters.
    centerPoint = adsk.core.Point3D.create(F_Pos, 0, 0)
    X_AxisPoint = adsk.core.Point3D.create(F_Pos + Major_X / 2, 0, 0)
    Y_AxisPoint = adsk.core.Point3D.create(F_Pos, Minor_Y / 2, 0)    
# Create the ellipse.
    ellipses = sketch_Profile.sketchCurves.sketchEllipses
    ellipses.add(centerPoint, X_AxisPoint, Y_AxisPoint)
##########################################################################
def DrawRectangle(sketch_Profile, F_Rad1, Crect_Wid, Crect_Ht, Cposition, CPosRect):
    F_Wid1 = float(Crect_Wid) * .1
    F_Ht1 = float(Crect_Ht) * .1
    F_Wid12 = F_Wid1 / 2.0
    F_Ht12 = F_Ht1 / 2.0
    F_Pos = F_Rad1
    X0 = F_Pos             # default 3 Horizontal position Outside edge
    X1 = F_Pos + F_Wid1
    if Cposition == '1':
        X0 = F_Pos - F_Wid1
    elif Cposition == '2':
        X0 = F_Pos - F_Wid12
    X1 = X0 + F_Wid1
    Y0 = 0                          # default 3 vertical position Bottom
    Y1 = -F_Ht1
# 1 = Top, 2 = Middle 3, = Bottom
    if CPosRect == '1':
        Y0 = F_Ht1
        Y1 = 0
    elif CPosRect == '2':
        Y0 = -F_Ht12
        Y1 = F_Ht12
    P1 = adsk.core.Point3D.create(X0, Y0, 0)
    P2 = adsk.core.Point3D.create(X1, Y0, 0)
    P3 = adsk.core.Point3D.create(X1, Y1, 0)
    P4 = adsk.core.Point3D.create(X0, Y1, 0)
    points = [P1, P2, P3, P4, P1]              # Create a list of points for single thread profile
    draw_lines_between_points(sketch_Profile, points, 0)
    X_Pts = [X0 + F_Wid12, X1]
    return (X_Pts)
##########################################################################
def DrawStar(sketch_Profile, F_Pos, outer_radius, inner_radius, num_points, CvertPos):
    centerX = F_Pos             # Center X coordinate of Star
    centerY = 0
    points = []
    initialAngle = SetStartAngle(CvertPos)
# Calculate the points of the star
    angle = 2 * math.pi / (num_points * 2)
    for i in range(num_points * 2):
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = centerX + radius * math.cos(i * angle + initialAngle)
        y = centerY + radius * math.sin(i * angle + initialAngle)
        points.append(adsk.core.Point3D.create(x, y, 0))
# Create the lines between the points
    lines = sketch_Profile.sketchCurves.sketchLines
    for i in range(num_points * 2):
        lines.addByTwoPoints(points[i], points[(i + 1) % (num_points * 2)])
##########################################################################
def DrawThreads(subComp1, OD, Pitch, PitHlx, Ht, sPts, G_Rail, RL_thread, iST_Char, RL_Check, iflag, iTY_Char):
    try:
        Ht1 = Ht * .1
        PitHlx1 = PitHlx * .1
        Rad = OD / 2.0
        pts = calcPts(OD, Pitch, PitHlx1)
        P00 = pts[0]
        P1 = pts[1]
        P2 = pts[2]
        P3 = pts[3]
        P4 = pts[4]
        P5 = pts[5]
        X0 = pts[6]                     # Have to do this way, because setting this to global in
        R_Min = pts[7]                  # calcPts(0) does not seem to work & does not make sense to me
        i_Error = 0
        if RL_Check == 'Y' and iflag == 1:
            P100 = adsk.core.Point3D.create(P1.x, P1.y + 1.0, 0)
            P101 = P1
            P102 = P2
            P103 = P3
            P104 = P4
            P105 = P5
            points = [P100, P101, P102, P103, P104, P105]
            Vertex_Pts = Real_offset(points)
            P1 = Vertex_Pts[0]
            P2 = Vertex_Pts[1]
            P3 = Vertex_Pts[2]
            P4 = Vertex_Pts[3]
            P22_y = -(PitHlx1 - P2.y)       # fusion 360 is backwards on negative/positive numbers here, so we need a negative number here
                                            # This took me a while to debug because of this
            X0 = P1.x - 0.01
            R_Min1 = X0
            R_Min = R_Min1 + .01
            Rad = P2.x * 10.0
            P00 = adsk.core.Point3D.create(X0,P1.y,0)
            P5 = adsk.core.Point3D.create(P4.x, P1.y - PitHlx1, 0)
            P4_y = abs(P4.y)            # Make positive to be less confusing in If Statement
            P5_y = abs(P5.y)
# We need to readjust P4 to the intersection point between line P4 to P5 & P5 to P2 extended by the Helix Pitch distance
            if P5_y < P4_y:
                if G_Rail != 'L' and G_Rail != 'P':
                    P22 = adsk.core.Point3D.create(P2.x, P22_y, 0)
# Calculate direction vectors
                    P45 = findIntersection(P3, P4, P5, P22)
                    i_Error = 1
                    Err_Dist = (P4_y - P5_y) * 10.0
                    S_Dist = "{:.4f}".format(Err_Dist)
                    msg = f'Female Profiles will overlap with using Real Offsets<br>Try increasing Helix Pitch, decreasing M/F Thread Gap<br>or UNCHECK Use Real Offset of Threads<br><br>Overlap Distance = {S_Dist}mm<br>P45.x = {P45.x}    P45.y = {P45.y}'
                    ui.messageBox(msg,"Warning", adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)
# Create a new 3D sketch.
        sketches = subComp1.sketches
        xyPlane = subComp1.xYConstructionPlane
        sketch_Helix = sketches.add(xyPlane)
        sketch_Helix.name = "Sketch_Helix"
# Create sketch for the profile to sweep
        sketch_Profile = sketches.add(subComp1.xZConstructionPlane)
        sketch_Profile.name = "Thread_Profile"
        sketch_Profile.sketchCurves.sketchLines
        rev = int(Ht / PitHlx) + 1                   # How many revolutions of helix
        if G_Rail== 'L' or G_Rail == 'P':
            points = [P00, P1, P2, P3, P4]              # Create a list of points for single thread profile
            draw_lines_between_points(sketch_Profile, points, iflag)
        else:
            if i_Error == 1:
                points = [P00, P1, P2, P3, P45]                             # Next profile overlaps, so use intersection P45 instead of P4, P5
                draw_lines_between_points(sketch_Profile, points, iflag)    # Draw 1st thread profile before loop
                P1 = adsk.core.Point3D.create(P45.x, P45.y + PitHlx1, 0)     # Change P1 to vertically below P45 intersection Point
                points = [P1, P2, P3, P45]
            else:
                points = [P00, P1, P2, P3, P4, P5]                          # Create a list of points to start multiple thread profiles
                draw_lines_between_points(sketch_Profile, points, iflag)    # Draw 1st thread profile before loop
                points = [P1, P2, P3, P4, P5]
# Loop to change the Y coordinate of points
            for i in range(rev):
# on last iteration, we do not want to draw between point P4 & P5
                if i == rev-1:
                    points = [P1, P2, P3, P4]
                for point in points:
                    point.y -= PitHlx1
                draw_lines_between_points(sketch_Profile, points, iflag)    # Draw the next thread
                if i_Error == 1:
                    P4.y -= PitHlx1
        if i_Error == 1:
            P4.y += PitHlx1             # simplest way to fix off by one, since we add 1 too many in the loop
        P6 = adsk.core.Point3D.create(X0, P4.y, 0)                            # P6 is vertical to P00
        sketch_Profile.sketchCurves.sketchLines.addByTwoPoints(P4, P6)      # Draw short horizontal line to be perpendicular to P00
        sketch_Profile.sketchCurves.sketchLines.addByTwoPoints(P6, P00)     # close profile
        largest_profile = sketch_Profile.profiles.item(0)
        if i_Error == 1:
# Get the profiles in the sketch
            profiles = sketch_Profile.profiles
            #num_profiles = profiles.count
# Initialize variables to track the largest profile and its area
            largest_profile = None
            largest_area = 0
# Iterate through each profile to find the one with the largest area
            for prof in profiles:
# Calculate the area of the profile
                area_properties = prof.areaProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
                area = area_properties.area
# Check if this profile has the largest area so far
                if area > largest_area:
                    largest_area = area
                    largest_profile = prof
# The 0.0 is a filler, because we need the minimum radius sent from Coil routine, but not for threads
        DrawHelix(subComp1,sketch_Helix, 0.0, Rad, PitHlx, Ht, Ht1, sPts, G_Rail, RL_thread, largest_profile, iflag)
# Now for the possible Single Rectangular pattern to create threads
        if G_Rail == 'P':
            DrawPatternThreads(subComp1, PitHlx, rev, 0)
        DrawCylinder(subComp1, sketch_Helix, Rad, R_Min, Ht1, Pitch, PitHlx, iflag, iTY_Char) # Only extrude the length of 1 helix revolution
        if iST_Char > 1:
            CopRot_Threads(subComp1, iST_Char)
    except Exception as e:
        ui.messageBox("Error: {}".format(traceback.format_exc()))
# Originally did the pattern this way until realizing  the pattern along path would be simpler
# def Old_DrawPatternThreads(subComp1, PitHlx, rev):
#     bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
#     numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used
#     targetBody = bsubComp1_bodies.item(numBodies-1)     # This should be the Nut just drawn
# # Create input entities for rectangular pattern
#     inputEntites = adsk.core.ObjectCollection.create()
#     inputEntites.add(targetBody)
# # Get x and y axes for rectangular pattern
#     xAxis = subComp1.xConstructionAxis
#     zAxis = subComp1.zConstructionAxis
# # Quantity and distance
#     quantityOne = adsk.core.ValueInput.createByString('1')      # quantity along X-Axis Not really used
#     distanceOne = adsk.core.ValueInput.createByString('1 cm')   # distance along X-Axis not really used
#     quantityTwo = adsk.core.ValueInput.createByString(str(rev))
#     distanceTwo = adsk.core.ValueInput.createByString(repr (PitHlx))
# # Create the input for rectangular pattern
#     rectangularPatterns = subComp1.features.rectangularPatternFeatures
#     rectangularPatternInput = rectangularPatterns.createInput(inputEntites, xAxis, quantityOne, distanceOne, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
# # Set the data for second direction
#     rectangularPatternInput.setDirectionTwo(zAxis, quantityTwo, distanceTwo)
# # Create the rectangular pattern
#     rectangularPatterns.add(rectangularPatternInput)
###################################################################################################
def DrawPatternThreads(subComp1, PitHlx, rev, iflag):
    PitHlx2 = PitHlx * .1
    bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
    numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used
    targetBody = bsubComp1_bodies.item(numBodies-1)     # This should be the Nut just drawnf
# Create input entities for rectangular pattern
    inputEntites = adsk.core.ObjectCollection.create()
    inputEntites.add(targetBody)
    path = subComp1.features.createPath(Vert_Line)
    General_Precision = preferences.unitAndValuePreferences.generalPrecision        # Get current precision
    preferences.unitAndValuePreferences.generalPrecision = 9                    # Set to maximum of 9 before running the pathPatterns code
    patternQuantity = adsk.core.ValueInput.createByReal(rev)
    patternDistance = adsk.core.ValueInput.createByReal(PitHlx2)
    pathPatterns = subComp1.features.pathPatternFeatures
    pathPatternInput = pathPatterns.createInput(inputEntites, path, patternQuantity, patternDistance, adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
# Create the path pattern
    pathPatterns.add(pathPatternInput)
# Combine them all together if this routine was called from Coil Routine
    if iflag == 1:
        panel_comb_fea = subComp1.features.combineFeatures
        tool_bodies_oc = adsk.core.ObjectCollection.createWithArray(
            [subComp1.bRepBodies[i] for i in range(1, subComp1.bRepBodies.count)]
        )
        comb_input: adsk.fusion.CombineFeatureInput = panel_comb_fea.createInput(
            subComp1.bRepBodies[0],
            tool_bodies_oc
        )
        comb_input.isKeepToolBodies = False
        comb_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        panel_comb_fea.add(comb_input)
    preferences.unitAndValuePreferences.generalPrecision = General_Precision        # Set precision back to what user had
###################################################################################################
# find intersection point of Line P01, P02 and P03, P04
def findIntersection(P01, P02, P03, P04):
    x1 = P01.x
    y1 = P01.y
    x2 = P02.x
    y2 = P02.y
    x3 = P03.x
    y3 = P03.y
    x4 = P04.x
    y4 = P04.y
    px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ) 
    py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
    return(adsk.core.Point3D.create(px, py, 0))
# Calculate the coefficients for the lines
def calculate_intersection(P3, P4, P5, P22):
    A1 = abs(P4.y) - abs(P3.y)
    B1 = P3.x - P4.x
    C1 = (A1 * P3.x) + (B1 * abs(P3.y))
    A2 = abs(P22.y) - abs(P5.y)
    B2 = P5.x - P22.x
    C2 = (A2 * P5.x) + (B2 * abs(P5.y))  
# Calculate the determinant
    det = A1 * B2 - A2 * B1
    if det == 0:
        return None  # Lines are parallel and do not intersect
# Calculate the intersection point
    x = (B2 * C1 - B1 * C2) / det
    y = (A1 * C2 - A2 * C1) / det
    return(adsk.core.Point3D.create(x, y, 0))
def CopRot_Threads(subComp1, iST_Char):
    rot_Array = [180, 90]
    icount = 1                  # one time thru loop if iST_Char = 2
    if iST_Char == 4:
        icount = 2              # two times thru loop if 1St_Char = 4
    i = 0
    while i < icount:
        bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
        numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used
        baseBody = bsubComp1_bodies.item(numBodies-1)       # Use the last body in the collection
# Copy/paste bodies
        subComp1.features.copyPasteBodies.add(baseBody)     # Copy & paste the body
        baseBodyCopy = bsubComp1_bodies.item(numBodies)     # Get the copied body
        rot_Angle = rot_Array[i]
        angle = math.radians(rot_Angle)
        P_Org = adsk.core.Point3D.create(0, 0, 0)
# Rotate the copied body 90 degrees around the Z-axis
        moveFeats = subComp1.features.moveFeatures
        inputEnts = adsk.core.ObjectCollection.create()
        inputEnts.add(baseBodyCopy)
        zAxis = subComp1.zConstructionAxis
        transform = adsk.core.Matrix3D.create()
        transform.setToRotation(angle, zAxis.geometry.direction, P_Org)
        moveFeats = subComp1.features.moveFeatures
        moveFeatureInput = moveFeats.createInput(inputEnts, transform)
        moveFeats.add(moveFeatureInput)
# Combine the original and copied bodies
        combineFeats = subComp1.features.combineFeatures
        combineInput = combineFeats.createInput(baseBody, adsk.core.ObjectCollection.create())
        combineInput.toolBodies.add(baseBodyCopy)
        combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeats.add(combineInput)
        i = i + 1
def subtract_bodies(subComp1):
    try:
        bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
        numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used, should be 3
        target_body = bsubComp1_bodies.item(numBodies-1)    # This should be the Nut just drawn
        target_body.name = BodyNut_Name
        tool_body = bsubComp1_bodies.item(numBodies-2)        # This should be the threads to cut out
# Create a combine input
        combineFeatures = subComp1.features.combineFeatures
        tools = adsk.core.ObjectCollection.create()
        tools.add(tool_body)
        input: adsk.fusion.CombineFeatureInput = combineFeatures.createInput(target_body, tools)
        input.isNewComponent = False
        input.isKeepToolBodies = False
        input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combineFeatures.add(input)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
##########################################################################
def draw_lines_between_points(sketch, points, iflag):
    for i in range(len(points)-1):
        sketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[i+1])
def get_current_folder():
    return os.path.dirname(os.path.abspath(__file__))
def file_exists(file_path):
    return os.path.exists(file_path)
def read_variables_from_text_file(Fname):
    variables = {}
    DialogName = open(Fname, 'r')
# Read variables from the text file
    with DialogName as file:
        variables['diameter'] = file.readline().strip()
        variables['pitch'] = file.readline().strip()
        variables['height'] = file.readline().strip()
        variables['angleTop'] = file.readline().strip()
        variables['angleBot'] = file.readline().strip()
        variables['splinePts'] = file.readline().strip()
        variables['GR_Char'] = file.readline().strip()
        variables['RL_Char'] = file.readline().strip()
    DialogName.close
    return variables
# Executed when add-in is run.
def start():
# Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
# Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)
# Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
# Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
# Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
# Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED
# Executed when add-in is stopped.
def stop():
# Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
# Delete the button command control
    if command_control:
        command_control.deleteMe()
# Delete the command definition
    if command_definition:
        command_definition.deleteMe()
def is_valid_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
def is_valid_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False       
### $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ###
# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
### $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ###
def command_created(args: adsk.core.CommandCreatedEventArgs):
# General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')
    global Fname
    global EFname
    global CFname
    global csvData
    global pitHelix
    global Thread_Wid
    global Thread_Ht
    global Thread_EWid
    global Thread_EHt
    global _Ediameter
    global _Epitch
    global _EpitHelix

    global tabCmdInput3
    global dropdown0CommandInput
    global dropdownInputEM
    global dropdownCommand_MInput
    global dropdownCommand_EInput
    global dropdownInput3
    global dropdownInput6
    global Metdata
    global Engdata
    global _diameter
    global _pitch
    global _pitHelix
    global _angleTop
    global _angleBot
    global _BoltFlat_Dia
    global _BoltHd_Ht
    global _NutFlat_Dia
    global _NutHd_Ht
    global _Cham_Wid
    global _Thread_Wid
    global _Thread_Ht
    global _MF_Gap
    global _Cham_EWid
    global _Thread_EWid
    global _Thread_EHt
    global group_Minput
    global group_Einput
    global group_M2input
    global group_E2input

    global _BoltFlat_EDia
    global _BoltHd_EHt
    global _NutFlat_EDia
    global _NutHd_EHt

    #global CoilType         # Type of Coil to Draw
    #global Cdiameter        # Diameter of Coil
    #global Crevs            # Number of Coil Revolutions
    #global Cheight          # Height of Coil
    #global Cpitch           # Pitch of Coil
    #global Cangle           # Coil Angle (0 = no angle)
    #global CsplinePts       # Number of Spline points per revolution for Coil
    global GR_Char          # GuideRail Type Helix, LongHelix or Pattern
    global GRC_Char         # Coil GuideRail Type LongHelix or Pattern
                            # Pattern will not work with Spiral or angle used with other coil types
    global Cdia_Sect        # Diameter of Circle or Polygon Profile for Coil
    #global CvertPos        # polygon vertext position
    #global CpolySides       # Number of Sides for Polygon Profile
    #global CellipseX        # Ellipse X Diameter
    #global CellipseY        # Ellipse Y Diameter (actually the along Z-axis if looking in 3D)
    #global Crect_Wid        # Width of Rectangle Profile
    #global Crect_Ht         # Height of Rectangle Profile
    #global CStarOut_Rad     # Outside Radius of Star Profile
    #global CStarIn_Rad      # Inside Radius of Star Profile
    #global CStar_Num        # Number of Star Points
    #global CSec_Type         # Profile Section type, 1 (Circle), 2 (Polygon), 3 (Rectangle) or 4 (Star)
    #global Cposition        # 1st character is 1 (inside), 2 (On Center) or 3 (Outside)
    #global CPosRect         # Rectangle Profile vertical position 1 = Top, 2 = Middle, 3 = Bottom
    #global _Cdia_Sect
    #global _Crect_Wid
    #global _Crect_Ht
    global group_T3_1_input
    global group_T3_2_input
    global group_T3_3_input
    #global _CStarOut_Rad
    #global _CStarIn_Rad
    #global _CStar_Num
# https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    current_folder = get_current_folder()           #Get the folder this program is located in

    unitsMgr = app.activeProduct.unitsManager
    defaultUnits = unitsMgr.defaultLengthUnits  # Returns the default length unit, e.g., "cm" or "in"
    
    ME_Units = 'M'
    if defaultUnits == 'in' or defaultUnits == 'ft':
        ME_Units = 'E'
    cmd = args.command    
    inputs = cmd.commandInputs
    cmd.setDialogInitialSize(400, 780)
# Create tab input 1
    tabCmdInput1 = inputs.addTabCommandInput('_Threads', 'Threads')
    tab1ChildInputs = tabCmdInput1.children
# Create tab input 2
    tabCmdInput2 = inputs.addTabCommandInput('_BoltNut', 'Bolts and Nuts')
    tab2ChildInputs = tabCmdInput2.children
# Create tab input 3
    tabCmdInput3 = inputs.addTabCommandInput('_Coils', 'Coil Options')
    tab3ChildInputs = tabCmdInput3.children
    # dropdownInput4 = tab3ChildInputs.addDropDownCommandInput('CoilType', 'Coil Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    # dropdown4Items = dropdownInput4.listItems
    # dropdown4Items.add('1 Revolution and Height', False, '')
    # dropdown4Items.add('2 Revolution and Pitch', False, '')
    # dropdown4Items.add('3 Height and Pitch', False, '')
    # dropdown4Items.add('4 Spiral', False, '')
    # I_CoilType = int(CoilType) - 1
    # dropdown4Items[I_CoilType].isSelected = True
    #dropdownCommand_MInput = childM.addDropDownCommandInput('MetType', 'Metric Thread Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    #        Met_ID = dropdownCommand_MInput.selectedItem.index
    Fname = current_folder + '\\' + 'DialogInput_V9.txt'     # This is the Default Metric Input file from previous entries
    EFname = current_folder + '\\' + 'EDialogInput_V9.txt'   # This is the Default English Input file from previous entries
    CFname = current_folder + '\\' + 'Coil_DialogInput_V10.txt'
    if file_exists(Fname):
        DialogName = open(Fname, 'r')
# Read variables from the text file if it exists
        with DialogName as f:
            reader = list(csv.reader(f))
        DialogName.close
        for csvData in reader:
# Read all the metric variables in from last dialog file
            diameter = csvData[0]
            pitch = csvData[1]
            pitHelix = csvData[2]
            height = csvData[3]
            angleTop = csvData[4]
            angleBot = csvData[5]
            splinePts = csvData[6]
            GRM_Char = csvData[7]
            RL_Char = csvData[8]
            ST_Char = csvData[9]
            TYM_Char = csvData[10]

            Bolt_Sides = csvData[11]
            BoltFlat_Dia = csvData[12]
            BoltHd_Ht = csvData[13]
            Nut_Sides = csvData[14]
            NutFlat_Dia = csvData[15]
            NutHd_Ht = csvData[16]
            MF_Gap = csvData[17]
            CT_Check = csvData[18]          # Chamfer Top of Threads
            CN_Check = csvData[19]          # Chamfer Both ends of Nut
            RL_Check = csvData[20]
            Cham_Wid = csvData[21]
            Thread_Wid = csvData[22]
            Thread_Ht = csvData[23]
# Metric File does not exist, so set the defaults to these
    else:
        diameter = '6'
        pitch = '1'
        pitHelix = '1'
        height = '10'
        angleTop = '30'
        angleBot = '30'
        splinePts = '18'
        GRM_Char = 'P'
        RL_Char = 'R'
        ST_Char = '1'
        TYM_Char = '5'
 
        Bolt_Sides = '6'
        BoltFlat_Dia = '10'
        BoltHd_Ht = '4'
        Nut_Sides = '6'
        NutFlat_Dia = '10'
        NutHd_Ht = '5'
        MF_Gap = '0.3'
        CT_Check = 'Y'
        CN_Check = 'Y'
        RL_Check = 'N'
        Cham_Wid = '1.015'
        Thread_Wid = '0.6766'
        Thread_Ht = '0.9375'
    if file_exists(EFname):
        DialogName = open(EFname, 'r')
# Read variables from the text file if it exists
        with DialogName as f:
            reader = list(csv.reader(f))
        DialogName.close
        for csvData in reader:
            Ediameter = csvData[0]
            Epitch = csvData[1]                     # Pitch is Threads per inch (TPI) in English
            EpitHelix = csvData[2]
            Eheight = csvData[3]
# only overwrite these variables if we are initially set to English Units
            if ME_Units == 'E':
                angleTop = csvData[4]
                angleBot = csvData[5]
                splinePts = csvData[6]
                RL_Char = csvData[8]
                ST_Char = csvData[9]
                Bolt_Sides = csvData[11]
                Nut_Sides = csvData[14]
                MF_Gap = csvData[17]
                CT_Check = csvData[18]          # Chamfer Top of Threads
                CN_Check = csvData[19]          # Chamfer Both ends of Nut
                RL_Check = csvData[20]
            GRE_Char = csvData[7]
            TYE_Char = csvData[10]
            BoltFlat_EDia = csvData[12]
            BoltHd_EHt = csvData[13]
            NutFlat_EDia = csvData[15]
            NutHd_EHt = csvData[16]
            Cham_EWid = csvData[21]
            Thread_EWid = csvData[22]
            Thread_EHt = csvData[23]
# File does not exist, so set the defaults to these
#Metric		Diameter	TPI	Metric OD mm	Metric Pitch	Hex Bolt Flat Diameter	Hex Head Thickness	Hex Nut Thickness	Chamfer Width	Thread Width	Thread Height	Thread Angle
#E 1/4-20 UNC	0.25		20	6.35		1.27		0.4375			0.163			0.21875			1.0311		0.6874		0.9525		30
    else:
        Ediameter = "0.25"
        Epitch = "20"
        EpitHelix = "20"
        Eheight = '1.0'
# only overwrite these variables if we are initially set to English Units
        if ME_Units == 'E':
            angleTop = '30'
            angleBot = '30'
            splinePts = '18'
            RL_Char = 'R'
            ST_Char = '1'
            Bolt_Sides = '6'
            Nut_Sides = '6'
            MF_Gap = '0.3'
            CT_Check = 'Y'
            CN_Check = 'Y'
            RL_Check = 'N'
        GRE_Char = 'P'
        TYE_Char = '5'
        BoltFlat_EDia = '.4375'
        BoltHd_EHt = '.156'
        NutFlat_EDia = '.4375'
        NutHd_EHt = '.219'
        Cham_EWid = '0.0406'
        Thread_EWid = '0.0271'
        Thread_EHt = '0.0375'
    if file_exists(CFname):
        csvData = None
        DialogName = open(CFname, 'r')
# Read variables from the text file if it exists
        with DialogName as f:
            reader = list(csv.reader(f))
        DialogName.close
        for csvData in reader:
            CoilType = csvData[0]
            Cdiameter = csvData[1]
            Crevs = csvData[2]
            Cheight = csvData[3]
            Cpitch = csvData[4]
            Cangle = csvData[5]
            CsplinePts = csvData[6]
            GRC_Char = csvData[7]
            CSec_Type = csvData[8]
            Cposition = csvData[9]
            Cdia_Sect = csvData[10]
            CpolySides = csvData[11]
            CvertPos = csvData[12]
            CellipseX = csvData[13]
            CellipseY = csvData[14]
            Crect_Wid = csvData[15]
            Crect_Ht = csvData[16]
            CPosRect = csvData[17]
            CStarOut_Rad = csvData[18]
            CStarIn_Rad = csvData[19]
            CStar_Num = csvData[20]
    else:
        CoilType = '2'
        Cdiameter = '24.0'
        Crevs = '3'
        Cheight = height
        Cpitch = pitHelix
        Cangle = '0'
        CsplinePts = '20'
        GRC_Char = 'L'
        CSec_Type = '1'
        Cposition = '2'
        Cdia_Sect = '2.0'
        CpolySides = '6'
        CvertPos = '1'
        CellipseX = '1.0'
        CellipseY = '2.0'
        Crect_Wid = '3'
        Crect_Ht = '6'
        CPosRect = '2'
        CStarOut_Rad = '5'
        CStarIn_Rad = '2.5'
        CStar_Num = '6'
    in_err = 0
    if not is_valid_float(diameter):
        diameter = '6'
        in_err = 100
    if not is_valid_float(pitch):
        pitch = '1'
        in_err = 101
    if not is_valid_float(pitHelix):
        pitHelix = '1'
        in_err = 102
    if not is_valid_float(height):
        height = '5'
        in_err = 103
    if not is_valid_float(angleTop):
        angleTop = '30'
        in_err = 104
    if not is_valid_float(angleBot):
        angleBot = '30'
        in_err = 105
    if not is_valid_int(splinePts):
        splinePts = '18'
        in_err = 106
    if GRM_Char != 'H' and GRM_Char != 'P' and GRM_Char != 'L':
        GRM_Char = 'P'
        in_err = 107
    if GRE_Char != 'H' and GRE_Char != 'P' and GRE_Char != 'L':
        GRE_Char = 'P'
        in_err = 108
    if RL_Char != 'R' and RL_Char != 'L':
        RL_Char = 'R'
        in_err = 109
    if ST_Char != '1' and ST_Char != '2' and ST_Char != '4':
        ST_Char = '1'
        in_err = 110
    if CT_Check != 'Y' and CT_Check != 'N':
        CT_Check = 'Y'
        in_err = 111
    if CN_Check != 'Y' and CN_Check != 'N':
        CN_Check = 'Y'
        in_err = 112
    if RL_Check != 'Y' and RL_Check != 'N':
        RL_Check = 'Y'
        in_err = 113
    if not is_valid_int(TYM_Char):
        TYM_Char = '5'
        in_err = 114
    else:
        if int(TYM_Char) > 6 or int(TYM_Char) < 1:
            TYM_Char = '5'
            in_err = 115
    if not is_valid_int(TYE_Char):
        TYE_Char = '5'
        in_err = 116
    else:
        if int(TYE_Char) > 6 or int(TYE_Char) < 1:
            TYE_Char = '5'
            in_err = 117
    if not is_valid_int(Bolt_Sides):
        Bolt_Sides = '6'
        in_err = 118
    if not is_valid_float(BoltFlat_Dia):
        BoltFlat_Dia = '10'
        in_err = 119
    if not is_valid_float(BoltHd_Ht):
        BoltHd_Ht = '4'
        in_err = 120
    if not is_valid_int(Nut_Sides):
        Nut_Sides = '6'
        in_err = 121
    if not is_valid_float(NutFlat_Dia):
        NutFlat_Dia = '10'
        in_err = 122
    if not is_valid_float(NutHd_Ht):
        NutHd_Ht = '5'
        in_err = 123
    if not is_valid_float(MF_Gap):
        MF_Gap = '.3'
        in_err = 124
    if not is_valid_float(Cham_Wid):
        Cham_Wid = '1.015'
        in_err = 125
    if not is_valid_float(Thread_Wid):
        Thread_Wid = '0.6766'
        in_err = 126
    if not is_valid_float(Thread_Ht):
        Thread_Ht = '0.9375'
        in_err = 127
    if ME_Units == 'M':
        TY_Char = TYM_Char
        GR_Char = GRM_Char
    else:
        TY_Char = TYE_Char
        GR_Char = GRE_Char
# If there was an error in the input data, write out the default values for that data
    if in_err > 0:
        BoltNut = Bolt_Sides + "," + BoltFlat_Dia + "," + BoltHd_Ht + "," + Nut_Sides + "," + NutFlat_Dia + "," + NutHd_Ht + "," + MF_Gap + "," + CT_Check + "," + CN_Check + "," + RL_Check + "," + Cham_Wid + "," + Thread_Wid + "," + Thread_Ht
        OutString = diameter +',' + pitch +',' + pitHelix + ',' + height +',' + angleTop +',' + angleBot +',' + splinePts +',' + GR_Char +',' + RL_Char + ',' + ST_Char + ',' + TYM_Char + ',' + BoltNut
        with open(Fname, 'w') as csvfile:
            csvfile.write(OutString)
        csvfile.close
# Create a dropdown command input
    dropdown0CommandInput = tab1ChildInputs.addDropDownCommandInput('WhatType', 'Threads or Coils to Create:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown0Items = dropdown0CommandInput.listItems
    dropdown0Items.add('1 - Single Thread Only', False, '')
    dropdown0Items.add('2 - Bolt Thread', False, '')
    dropdown0Items.add('3 - Threads M/F', False, '')
    dropdown0Items.add('4 - Nut Thread', False, '')
    dropdown0Items.add('5 - Bolt & Nut Threads', False, '')
    dropdown0Items.add('6 - Coils', False, '')
    I_TY_Char = int(TY_Char) - 1
    dropdown0Items[I_TY_Char].isSelected = True
    dropdownInputEM = tab1ChildInputs.addDropDownCommandInput('EnglishMetric', 'English or Metric', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdownEMItems = dropdownInputEM.listItems
# Test what was used for the Thread direction on previous run dropdownCommand_MInput
    if ME_Units == 'E':
        dropdownEMItems.add('English', True, '')
        dropdownEMItems.add('Metric', False, '')
    else:
        dropdownEMItems.add('English', False, '')
        dropdownEMItems.add('Metric', True, '')
########################     Metric Section Below  ########################
    group_Minput = tab1ChildInputs.addGroupCommandInput('group_Minput', 'Metric Section')
    group_Minput.isExpanded = False
    childM = group_Minput.children
    dropdownCommand_MInput = childM.addDropDownCommandInput('MetType', 'Metric Thread Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    #        Met_ID = dropdownCommand_MInput.selectedItem.index
    MFname = current_folder + '\\' + 'metric_V3.csv'        #Standard Metric sizes from M3 - M30
    if file_exists(MFname):
# Read the Metric Sizes file
        file = open(MFname, "r")
        Metdata = list(csv.reader(file, delimiter=","))
        file.close()
        outstr = ""
        j = len(Metdata)
        dropdownMItems = dropdownCommand_MInput.listItems
        for i in range(1,j):
            outstr= Metdata[i][0] + Metdata[i][1]+ "x" + Metdata[i][2]
            dropdownMItems.add(outstr, False, '')                       #Add this Metric size to the Dropdownlist
    _diameter = childM.addTextBoxCommandInput('diameter','Diameter (mm): ',diameter, 1, False )
    _pitch = childM.addTextBoxCommandInput('pitch', 'Thread Pitch (mm): ', pitch, 1, False)
    _pitHelix = childM.addTextBoxCommandInput('pitHelix', 'Helix Pitch (mm): ', pitHelix, 1, False)
    childM.addTextBoxCommandInput('height', 'Height (mm): ', height, 1, False)
    _Cham_Wid = childM.addTextBoxCommandInput('Cham_Wid', 'Chamfer Width (mm): ', Cham_Wid, 1, False)
    _Thread_Wid = childM.addTextBoxCommandInput('Thread_Wid', 'Thread Width (mm): ', Thread_Wid, 1, True)
    _Thread_Ht = childM.addTextBoxCommandInput('Thread_Ht', 'Thread Height (mm): ', Thread_Ht, 1, True)
########################     Metric Section Above  ########################
########################    English Section Below  ########################
    group_Einput = tab1ChildInputs.addGroupCommandInput('group_Einput', 'English Section')
    group_Einput.isExpanded = False
    childE = group_Einput.children
    dropdownCommand_EInput = childE.addDropDownCommandInput('EngType', 'English Thread Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    EngFname = current_folder + '\\' + 'English_V3.csv'        # Standard English sizes from #6 - 2"
    if file_exists(EngFname):
# Read the English Sizes file
        file = open(EngFname, "r")
        Engdata = list(csv.reader(file, delimiter=","))
        file.close()
        outstr = ""
        j = len(Engdata)
        dropdownEItems = dropdownCommand_EInput.listItems
        for i in range(1,j):
            outstr= Engdata[i][0] + Engdata[i][1]+ "x" + Engdata[i][2]
            dropdownEItems.add(outstr, False, '')                       #Add this Metric size to the Dropdownlist
    _Ediameter = childE.addTextBoxCommandInput('Ediameter','Diameter (In): ',Ediameter, 1, False )
    _Epitch = childE.addTextBoxCommandInput('Epitch', 'Threads Per Inch (In): ', Epitch, 1, False)
    _EpitHelix = childE.addTextBoxCommandInput('EpitHelix', 'Helix Per Inch (In): ', EpitHelix, 1, False)
    childE.addTextBoxCommandInput('Eheight', 'Height (In): ', Eheight, 1, False)
    _Cham_EWid = childE.addTextBoxCommandInput('Cham_EWid', 'Chamfer Width (In): ', Cham_EWid, 1, False)
    _Thread_EWid = childE.addTextBoxCommandInput('Thread_EWid', 'Thread Width (In): ', Thread_EWid, 1, True)
    _Thread_EHt = childE.addTextBoxCommandInput('Thread_EHt', 'Thread Height (In): ', Thread_EHt, 1, True)
########################  English Section Above  ########################
    _angleTop = tab1ChildInputs.addTextBoxCommandInput('angleTop', 'Top Angle (deg): ', angleTop, 1, False)
    _angleBot = tab1ChildInputs.addTextBoxCommandInput('angleBot', 'Bottom Angle (deg): ', angleBot, 1, False)
    tab1ChildInputs.addTextBoxCommandInput('splinePts', 'Helix Spline Points: ', splinePts, 1, False)
    tab2ChildInputs.addTextBoxCommandInput('Bolt_Sides', '# of Bolt Head Sides: ', Bolt_Sides, 1, False)
    tab2ChildInputs.addTextBoxCommandInput('Nut_Sides', '# of Sides of Nut: ', Nut_Sides, 1, False)
########################  Metric Tab2 Section Below   ########################
    group_M2input = tab2ChildInputs.addGroupCommandInput('group_M2input', 'Metric Bolts/Nuts Section')
    group_M2input.isExpanded = False
    childM2 = group_M2input.children
    _BoltFlat_Dia = childM2.addTextBoxCommandInput('BoltFlat_Dia', 'Bolt Head Flat Dia: ', BoltFlat_Dia, 1, False)
    _BoltHd_Ht = childM2.addTextBoxCommandInput('BoltHd_Ht', 'Bolt Head Height: ', BoltHd_Ht, 1, False)
    _NutFlat_Dia = childM2.addTextBoxCommandInput('NutFlat_Dia', 'Nut Flat Dia: ', NutFlat_Dia, 1, False)
    _NutHd_Ht = childM2.addTextBoxCommandInput('NutHd_Ht', 'Nut Height: ', NutHd_Ht, 1, False)
########################  English Tab2 Section Below   ########################
    group_E2input = tab2ChildInputs.addGroupCommandInput('group_E2input', 'English Bolts/Nuts Section')
    group_E2input.isExpanded = False
    childE2 = group_E2input.children
    _BoltFlat_EDia = childE2.addTextBoxCommandInput('BoltFlat_EDia', 'Bolt Head Flat Dia: ', BoltFlat_EDia, 1, False)
    _BoltHd_EHt = childE2.addTextBoxCommandInput('BoltHd_EHt', 'Bolt Head Height: ', BoltHd_EHt, 1, False)
    _NutFlat_EDia = childE2.addTextBoxCommandInput('NutFlat_EDia', 'Nut Flat Dia: ', NutFlat_EDia, 1, False)
    _NutHd_EHt = childE2.addTextBoxCommandInput('NutHd_EHt', 'Nut Height: ', NutHd_EHt, 1, False)
# Create dropdown input with test list style.
    dropdownInput1 = tab1ChildInputs.addDropDownCommandInput('GuideRail', 'Helix, Pattern or Long Helix Guide:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown1Items = dropdownInput1.listItems
    if ME_Units == 'M':
        group_Minput.isExpanded = True
        group_M2input.isExpanded = True
    else:
        group_Einput.isExpanded = True
        group_E2input.isExpanded = True
# Test what was used for the guideline on previous run
# H = Single Helix & Threads complete length
# C = Center line Guide Rail                                We are disabling this for now, since it does not work well
# L = Long Helix complete length & Single thread profile
# P = Pattern of Single Helix & Single Thread copied for longer threads
    dropdown1Items.add('Helix', False, '')
    dropdown1Items.add('Pattern', False, '')
    dropdown1Items.add('LongHelix', False, '')
    if GR_Char == 'C' or GR_Char == 'H':
        dropdown1Items[0].isSelected = True
    elif GR_Char == 'P':
        dropdown1Items[1].isSelected = True
    elif GR_Char == 'L':
        dropdown1Items[2].isSelected = True
    dropdownInput2 = tab1ChildInputs.addDropDownCommandInput('RightLeft', 'Right or Left Threads', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown2Items = dropdownInput2.listItems
# Test what was used for the Thread direction on previous run
    if RL_Char == 'R':
        dropdown2Items.add('Right', True, '')
        dropdown2Items.add('Left', False, '')
    else:
        dropdown2Items.add('Right', False, '')
        dropdown2Items.add('Left', True, '')
    dropdownInput3 = tab1ChildInputs.addDropDownCommandInput('Starts', 'Number of Thread Starts', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown3Items = dropdownInput3.listItems
    dropdown3Items.add('1 Start', False, '')
    dropdown3Items.add('2 Start', False, '')
    dropdown3Items.add('4 Start', False, '')
    I_ST_Char = int(ST_Char) - 1
    dropdown3Items[I_ST_Char].isSelected = True
    if CT_Check == 'Y':
        tab1ChildInputs.addBoolValueInput('_ChamThread', 'Chamfer Top of Thread', True, '', True)
    else:
        tab1ChildInputs.addBoolValueInput('_ChamThread', 'Chamfer Top of Thread', True, '', False)
    if CN_Check == 'Y':
        tab1ChildInputs.addBoolValueInput('_ChamNut', 'Chamfer Nut', True, '', True)
    else:
        tab1ChildInputs.addBoolValueInput('_ChamNut', 'Chamfer Nut', True, '', False)
    _MF_Gap = tab1ChildInputs.addTextBoxCommandInput('MF_Gap', 'M/F thread Gap (mm): ', MF_Gap, 1, False)
    if RL_Check == 'Y':
        tab1ChildInputs.addBoolValueInput('_RealOffset', 'Use Real Offset of Threads', True, '', True)
    else:
        tab1ChildInputs.addBoolValueInput('_RealOffset', 'Use Real Offset of Threads', True, '', False)
##### Tab3 ################################################################################################
# 1 Revolution and Height (also has optional angle)
# 2 Revolution and Pitch (also has optional angle)
# 3 Height and Pitch (also has optional angle)
# 4 Spiral
    dropdownInput4 = tab3ChildInputs.addDropDownCommandInput('CoilType', 'Coil Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown4Items = dropdownInput4.listItems
    dropdown4Items.add('1 Revolution and Height', False, '')
    dropdown4Items.add('2 Revolution and Pitch', False, '')
    dropdown4Items.add('3 Height and Pitch', False, '')
    dropdown4Items.add('4 Spiral', False, '')
    I_CoilType = int(CoilType) - 1
    dropdown4Items[I_CoilType].isSelected = True
    tab3ChildInputs.addTextBoxCommandInput('Cdiameter','Coil Diameter (mm): ',Cdiameter, 1, False )
    tab3ChildInputs.addTextBoxCommandInput('Crevs','Coil Revolutions: ',Crevs, 1, False )
    tab3ChildInputs.addTextBoxCommandInput('Cheight', 'Coil Height (mm): ', Cheight, 1, False)
    tab3ChildInputs.addTextBoxCommandInput('Cpitch', 'Coil Pitch (mm): ', Cpitch, 1, False)
    tab3ChildInputs.addTextBoxCommandInput('Cangle', 'Coil Angle: ', Cangle, 1, False)
    tab3ChildInputs.addTextBoxCommandInput('CsplinePts', 'Coil Helix Spline Points: ', CsplinePts, 1, False)
    GR_Char = 'L'
# disabled for now, since for a lot of cases we have to use LongHelix
    # dropdownInput5 = tab3ChildInputs.addDropDownCommandInput('C_GuideRail', 'Pattern or Long Helix Coil Guide:', adsk.core.DropDownStyles.TextListDropDownStyle)
    # dropdown5Items = dropdownInput5.listItems
    # dropdown5Items.add('Pattern', False, '')
    # dropdown5Items.add('LongHelix', False, '')
    # if GRC_Char == 'P':
    #     dropdown5Items[0].isSelected = True
    # elif GRC_Char == 'L':
    #     dropdown5Items[1].isSelected = True
#dropdownCommand_MInput = childM.addDropDownCommandInput('MetType', 'Metric Thread Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdownInput6 = tab3ChildInputs.addDropDownCommandInput('CSec_Type', 'Section Type:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown6Items = dropdownInput6.listItems
    dropdown6Items.add('1 Circle', False, '')
    dropdown6Items.add('2 Polygon', False, '')
    dropdown6Items.add('3 Ellipse', False, '')
    dropdown6Items.add('4 Rectangle', False, '')
    dropdown6Items.add('5 Star', False, '')
    I_CSec_Type = int(CSec_Type) - 1
    dropdown6Items[I_CSec_Type].isSelected = True
    dropdownInput7 = tab3ChildInputs.addDropDownCommandInput('Cposition', 'Section Position:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown7Items = dropdownInput7.listItems
    dropdown7Items.add('1 Inside', False, '')
    dropdown7Items.add('2 On Center', False, '')
    dropdown7Items.add('3 Outside', False, '')
    I_Cposition =  int(Cposition) - 1
    dropdown7Items[I_Cposition].isSelected = True
    dropdownInput8 = tab3ChildInputs.addDropDownCommandInput('CvertPos', 'Vertex Position:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown8Items = dropdownInput8.listItems
    dropdown8Items.add('1 - Right vertex', False, '')
    dropdown8Items.add('2 - Top vertex', False, '')
    dropdown8Items.add('3 - Left vertex', False, '')
    dropdown8Items.add('4 - Bottom vertex', False, '')
    dropdown8Items.add('5 - 22.5Deg vertex (8 sided)', False, '')
    dropdown8Items.add('6 - 45.0Deg vertex (12 Sided)', False, '')
    I_VertPos = int(CvertPos) - 1
    dropdown8Items[I_VertPos].isSelected = True
    Cir_Chars = 'o' * 55
    tab3ChildInputs.addTextBoxCommandInput('C_Border1', '', Cir_Chars, 1, True) 
# Circle & Polygon Group
    group_T3_1_input = tab3ChildInputs.addGroupCommandInput('group_T3_1_input', 'Circle, Ellipse & Polygon Group')
    group_T3_1_input.isExpanded = False
    child_T3_1 = group_T3_1_input.children
    child_T3_1.addTextBoxCommandInput('Cdia_Sect','Section Diameter (mm): ',Cdia_Sect, 1, False )
    child_T3_1.addTextBoxCommandInput('CpolySides', '# of Sides of Polygon Section: ', CpolySides, 1, False)
    child_T3_1.addTextBoxCommandInput('CellipseX', 'Diameter of Ellipse on X-Axis (mm): ', CellipseX, 1, False)
    child_T3_1.addTextBoxCommandInput('CellipseY', 'Diameter of Ellipse on Y-Axis (mm): ', CellipseY, 1, False)
    Rect_Chars = '▮' * 55
    tab3ChildInputs.addTextBoxCommandInput('C_Border2', '', Rect_Chars, 1, True)
# Rectangle Group
    group_T3_2_input = tab3ChildInputs.addGroupCommandInput('group_T3_2_input', 'Rectangle Group')
    group_T3_2_input.isExpanded = False
    child_T3_2 = group_T3_2_input.children
    child_T3_2.addTextBoxCommandInput('Crect_Wid','Rectangle Width (mm): ',Crect_Wid, 1, False )
    child_T3_2.addTextBoxCommandInput('Crect_Ht','Rectangle Height (mm): ',Crect_Ht, 1, False )
    dropdownInput9 = child_T3_2.addDropDownCommandInput('CPosRect', 'Rectangle Position:', adsk.core.DropDownStyles.TextListDropDownStyle)
    dropdown9Items = dropdownInput9.listItems
    dropdown9Items.add('1 Top', False, '')
    dropdown9Items.add('2 Middle', False, '')
    dropdown9Items.add('3 Bottom', False, '')
    I_CPosRect = int(CPosRect) - 1
    dropdown9Items[I_CPosRect].isSelected = True
    Star_Chars = '✮' * 30
    tab3ChildInputs.addTextBoxCommandInput('C_Border3', '', Star_Chars, 1, True) 
# Star Group                                                                                 
    group_T3_3_input = tab3ChildInputs.addGroupCommandInput('group_T3_3_input', 'Star Group')
    group_T3_3_input.isExpanded = False
    child_T3_3 = group_T3_3_input.children
    child_T3_3.addTextBoxCommandInput('CStarOut_Rad','Outer Radius (mm): ',CStarOut_Rad, 1, False )
    child_T3_3.addTextBoxCommandInput('CStarIn_Rad','Inner Radius (mm): ',CStarIn_Rad, 1, False )
    child_T3_3.addTextBoxCommandInput('CStar_Num','Number of Star Points: ',CStar_Num, 1, False )
    group_T3_1_input.isExpanded = False
    group_T3_2_input.isExpanded = False
    group_T3_3_input.isExpanded = False
    I_Type = dropdownInput6.selectedItem.index
    if I_Type < 3:
        group_T3_1_input.isExpanded = True
    elif I_Type == 3:
        group_T3_2_input.isExpanded = True
    elif I_Type == 4:
        group_T3_3_input.isExpanded = True
# if Coils Options was selected last time, active that tab
    if TY_Char == '6':
        tabCmdInput3.activate()
# Set tab3 active when coils if coils option was selected last time.
    CalcThread(0)
# Connect to event handlers
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)                                                                                                 
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###
# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###                                                                                                      
def command_execute(args: adsk.core.CommandEventArgs):
# General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')
    global Body_Name
    global BodyNut_Name
# Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    Eng_ID = dropdownInputEM.selectedItem.index         # See if user changed the default to Metric or English units
    if Eng_ID == 0:
        ME_Units = 'E'
    else:
        ME_Units = 'M'
    angleTop: adsk.core.TextBoxCommandInput = inputs.itemById('angleTop')
    angleBot: adsk.core.TextBoxCommandInput = inputs.itemById('angleBot')
    splinePts: adsk.core.TextBoxCommandInput = inputs.itemById('splinePts')
    Bolt_Sides: adsk.core.TextBoxCommandInput = inputs.itemById('Bolt_Sides')
    Nut_Sides: adsk.core.TextBoxCommandInput = inputs.itemById('Nut_Sides')
    MF_Gap: adsk.core.TextBoxCommandInput = inputs.itemById('MF_Gap')                   # Making this mm for both English & Metric
    dropdownInput1 = inputs.itemById('GuideRail')
    GuideRail = dropdownInput1.selectedItem.name
    dropdownInput2 = inputs.itemById('RightLeft')
    RtLt = dropdownInput2.selectedItem.name
    dropdownInput3 = inputs.itemById('Starts')
    ST_Num = dropdownInput3.selectedItem.name
    dropdownInput0 = inputs.itemById('WhatType')
    TY_Char = dropdownInput0.selectedItem.name[0]           # 1st character of the string we test on
    _ChamThread: adsk.core.BoolValueCommandInput = inputs.itemById('_ChamThread')
    _ChamNut: adsk.core.BoolValueCommandInput = inputs.itemById('_ChamNut')
    _RealOffset: adsk.core.BoolValueCommandInput = inputs.itemById('_RealOffset')
    CT_Check = 'N'
    CN_Check = 'N'
    RL_Check = 'N'
########################################################################
############################# Coil Section #############################
########################################################################
    Cdiameter: adsk.core.TextBoxCommandInput = inputs.itemById('Cdiameter')
    Cpitch: adsk.core.TextBoxCommandInput = inputs.itemById('Cpitch')
    Cheight: adsk.core.TextBoxCommandInput = inputs.itemById('Cheight')
    CsplinePts: adsk.core.TextBoxCommandInput = inputs.itemById('CsplinePts')
    Crevs: adsk.core.TextBoxCommandInput = inputs.itemById('Crevs')
    Cangle: adsk.core.TextBoxCommandInput = inputs.itemById('Cangle')
    Crevs = Crevs.text
    Cangle = Cangle.text
    Cdiameter = Cdiameter.text
    Cpitch = Cpitch.text
    Cheight = Cheight.text
    CsplinePts = CsplinePts.text

    dropdownInput4 = inputs.itemById('CoilType')
    CoilType = dropdownInput4.selectedItem.name[0] 
    #dropdownInput5 = inputs.itemById('C_GuideRail')
    #GRC_Char = dropdownInput5.selectedItem.name[0]           # 1st character of the string we test on
    dropdownInput6 = inputs.itemById('CSec_Type')
    CSec_Type = dropdownInput6.selectedItem.name[0]
    dropdownInput7 = inputs.itemById('Cposition')
    Cposition = dropdownInput7.selectedItem.name[0]
    
# Circle & Polygon Group
    Cdia_Sect: adsk.core.TextBoxCommandInput = inputs.itemById('Cdia_Sect')
    CpolySides: adsk.core.TextBoxCommandInput = inputs.itemById('CpolySides')
    dropdownInput8 = inputs.itemById('CvertPos')
    Cdia_Sect = Cdia_Sect.text
    CpolySides = CpolySides.text
    CvertPos = dropdownInput8.selectedItem.name[0]
    CellipseX: adsk.core.TextBoxCommandInput = inputs.itemById('CellipseX')
    CellipseY: adsk.core.TextBoxCommandInput = inputs.itemById('CellipseY')
    CellipseX = CellipseX.text
    CellipseY = CellipseY.text
# Rectangle Group
    Crect_Wid: adsk.core.TextBoxCommandInput = inputs.itemById('Crect_Wid')
    Crect_Ht: adsk.core.TextBoxCommandInput = inputs.itemById('Crect_Ht')
    Crect_Wid = Crect_Wid.text
    Crect_Ht = Crect_Ht.text
    dropdownInput9 = inputs.itemById('CPosRect')
    CPosRect = dropdownInput9.selectedItem.name[0]          #1 = Top, 2 = Middle, 3 = Bottom
# Star Group
    CStarOut_Rad: adsk.core.TextBoxCommandInput = inputs.itemById('CStarOut_Rad')
    CStarIn_Rad: adsk.core.TextBoxCommandInput = inputs.itemById('CStarIn_Rad')
    CStar_Num: adsk.core.TextBoxCommandInput = inputs.itemById('CStar_Num')
    CStarOut_Rad = CStarOut_Rad.text
    CStarIn_Rad = CStarIn_Rad.text
    CStar_Num = CStar_Num.text
    if _ChamThread.value:
        CT_Check = 'Y'
    if _ChamNut.value:
        CN_Check = 'Y'
    if _RealOffset.value:
        RL_Check = 'Y'
    if ME_Units == "E":
        Ediameter: adsk.core.TextBoxCommandInput = inputs.itemById('Ediameter')
        Epitch: adsk.core.TextBoxCommandInput = inputs.itemById('Epitch')
        EpitHelix: adsk.core.TextBoxCommandInput = inputs.itemById('EpitHelix')
        Eheight: adsk.core.TextBoxCommandInput = inputs.itemById('Eheight')
        Cham_EWid: adsk.core.TextBoxCommandInput = inputs.itemById('Cham_EWid')
        BoltFlat_EDia: adsk.core.TextBoxCommandInput = inputs.itemById('BoltFlat_EDia')
        BoltHd_EHt: adsk.core.TextBoxCommandInput = inputs.itemById('BoltHd_EHt')
        NutFlat_EDia: adsk.core.TextBoxCommandInput = inputs.itemById('NutFlat_EDia')
        NutHd_EHt: adsk.core.TextBoxCommandInput = inputs.itemById('NutHd_EHt')
        Ediameter = Ediameter.text
        Epitch = Epitch.text
        EpitHelix = EpitHelix.text
        Eheight = Eheight.text
        Cham_EWid = Cham_EWid.text
        BoltFlat_EDia = BoltFlat_EDia.text
        BoltHd_EHt = BoltHd_EHt.text
        NutFlat_EDia = NutFlat_EDia.text
        NutHd_EHt = NutHd_EHt.text
# Not doing error checks just yet
        diameter = repr(float(Ediameter) * 25.4)             # Convert all English values to mm before processing the data
        pitch = repr((1.0 / float(Epitch)) * 25.4)
        pitHelix = repr((1.0 / float(EpitHelix)) * 25.4)
        height = repr(float(Eheight) * 25.4)

        Cham_Wid = repr(float(Cham_EWid) * 25.4)
        BoltFlat_Dia = repr(float(BoltFlat_EDia) * 25.4)
        BoltHd_Ht = repr(float(BoltHd_EHt) * 25.4)
        NutFlat_Dia = repr(float(NutFlat_EDia) * 25.4)
        NutHd_Ht = repr(float(NutHd_EHt) * 25.4)
    else:
        diameter: adsk.core.TextBoxCommandInput = inputs.itemById('diameter')
        pitch: adsk.core.TextBoxCommandInput = inputs.itemById('pitch')
        pitHelix: adsk.core.TextBoxCommandInput = inputs.itemById('pitHelix')
        height: adsk.core.TextBoxCommandInput = inputs.itemById('height')
        BoltFlat_Dia: adsk.core.TextBoxCommandInput = inputs.itemById('BoltFlat_Dia')
        BoltHd_Ht: adsk.core.TextBoxCommandInput = inputs.itemById('BoltHd_Ht')
        NutFlat_Dia: adsk.core.TextBoxCommandInput = inputs.itemById('NutFlat_Dia')
        NutHd_Ht: adsk.core.TextBoxCommandInput = inputs.itemById('NutHd_Ht')
        Cham_Wid: adsk.core.TextBoxCommandInput = inputs.itemById('Cham_Wid')
        diameter = diameter.text
        pitch = pitch.text
        pitHelix = pitHelix.text
        height = height.text
        Cham_Wid = Cham_Wid.text
        BoltFlat_Dia = BoltFlat_Dia.text
        BoltHd_Ht = BoltHd_Ht.text
        NutFlat_Dia = NutFlat_Dia.text
        NutHd_Ht = NutHd_Ht.text
    angleTop = angleTop.text
    angleBot = angleBot.text
    splinePts = splinePts.text
    Bolt_Sides = Bolt_Sides.text
    Nut_Sides = Nut_Sides.text
    MF_Gap = MF_Gap.text
    Ht = float(height)
# Make sure height is a positive number
    if Ht < 0:
        height = str(abs(Ht))
    GR_Char = 'C'
    RL_Char = 'R'
    iST_Char = 1
    if GuideRail == 'Helix':
        GR_Char = 'H'
    elif GuideRail == 'Pattern':
        GR_Char = 'P'
    elif GuideRail =='LongHelix':
        GR_Char = 'L'               # This option can really bog down fusion if there are a lot of threads
    if RtLt == 'Left':
        RL_Char = 'L'
    if ST_Num == '2 Start':
        iST_Char = 2
    elif ST_Num == '4 Start':
        iST_Char = 4      
    ST_Char = str (iST_Char)
    sPts = int(splinePts)
    start = time.time()
# Write back user inputs as defaults for next time
# Putting the code below in a subroutine does not use the global variables for some reason & it does not make any sense to me.
# If I print pitHelix and MF_Gap before this & put the following 6 lines in a subroutine, the subroutine will use the values from when it 1st read the DialogInput_V9.txt file & not current values
# so I have to duplicate the code to get it to work correctly.
    if ME_Units == 'M':
        BoltNut = Bolt_Sides + "," + BoltFlat_Dia + "," + BoltHd_Ht + "," + Nut_Sides + "," + NutFlat_Dia + "," + NutHd_Ht + "," + MF_Gap + "," + CT_Check + "," + CN_Check + "," + RL_Check + "," + Cham_Wid + "," + Thread_Wid + "," + Thread_Ht
        OutString = diameter +',' + pitch +',' + pitHelix + ',' + height +',' + angleTop +',' + angleBot +',' + splinePts +',' + GR_Char +',' + RL_Char + ',' + ST_Char + ',' + TY_Char + ',' + BoltNut
        with open(Fname, 'w') as csvfile:
            csvfile.write(OutString)
        csvfile.close
        Body_Name = "M" + diameter + "_" + pitch + "TPx" + pitHelix + "HPx" + height + "mm" + "_" + RL_Char + "_" + angleTop + "D_" + angleBot + "D_" + splinePts + "spts_" + GR_Char + "_Guide"
        OD = float(diameter)
        Pit = float(pitch)
        PitHlx = float(pitHelix)
        F_Height = float(height)
        F_Cham_Wid = float(Cham_Wid)
    else:
        BoltNut = Bolt_Sides + "," + BoltFlat_EDia + "," + BoltHd_EHt + "," + Nut_Sides + "," + NutFlat_EDia + "," + NutHd_EHt + "," + MF_Gap + "," + CT_Check + "," + CN_Check + "," + RL_Check + "," + Cham_EWid + "," + Thread_EWid + "," + Thread_EHt
        OutString = Ediameter +',' + Epitch +',' + EpitHelix + ',' + Eheight +',' + angleTop +',' + angleBot +',' + splinePts +',' + GR_Char +',' + RL_Char + ',' + ST_Char + ',' + TY_Char + ',' + BoltNut
        with open(EFname, 'w') as csvfile:
            csvfile.write(OutString)
        csvfile.close
        Body_Name = Ediameter + "_" + Epitch + "TPIx" + EpitHelix + "HTPIx" + Eheight + '"' + "_" + RL_Char + "_" + angleTop + "D_" + angleBot + "D_" + splinePts + "spts_" + GR_Char + "_Guide"
        OD = float(Ediameter) * 25.4
        Pit = (1.0 / float(Epitch)) * 25.4
        PitHlx = (1.0 / float(EpitHelix)) * 25.4
        F_Height = float(Eheight) * 25.4
        F_Cham_Wid = float(Cham_EWid) * 25.4
# Create New Component for all this geometry to start with
    Tstart = design.timeline.markerPosition
#TY_Char
# 1 - Single Thread Only
# 2 - Bolt Thread
# 3 - Threads M/F
# 4 - Nut Thread
# 5 - Bolt & Nut Threads
# 6 - Coils
    iTY_Char = int(TY_Char)
    if iTY_Char == 6:
        OutString1 = Cposition + ',' + Cdia_Sect + ',' + CpolySides + ',' + CvertPos + ',' + CellipseX + ',' + CellipseY + ',' + Crect_Wid +',' + Crect_Ht + ',' + CPosRect + ',' +  CStarOut_Rad + ',' + CStarIn_Rad + ',' + CStar_Num
        OutString = CoilType + ',' + Cdiameter +',' + Crevs + ',' + Cheight + ',' + Cpitch + ',' + Cangle + ',' + CsplinePts + ',' + GRC_Char + ',' + CSec_Type + ',' + OutString1
        with open(CFname, 'w') as csvfile:
            csvfile.write(OutString)
        csvfile.close
        Cspts = int(CsplinePts)
        Coil_Name = "Coil_" + Cdiameter
        subComp1 = CreateNewComponent(Coil_Name)
        DrawCoil(subComp1, CoilType, Cdiameter, CSec_Type, CpolySides, CellipseX, CellipseY, Cposition, CPosRect, Crect_Wid, Crect_Ht, CStarOut_Rad, CStarIn_Rad, CStar_Num, Cpitch, Crevs, Cheight, Cspts, GRC_Char, RL_Char, Cangle, CvertPos)
    else:
        subComp1 = CreateNewComponent(Body_Name)
        if iTY_Char != 4:
            DrawThreads(subComp1, OD, Pit, PitHlx, F_Height, sPts, GR_Char, RL_Char, iST_Char, RL_Check, 0, iTY_Char)
            if CT_Check == 'Y':
                ChamferTopThreads(subComp1, OD / 2, F_Height, F_Cham_Wid)
        if iTY_Char == 2 or iTY_Char == 5:
            DrawBoltHead(subComp1, float(BoltFlat_Dia),int(Bolt_Sides),float(BoltHd_Ht))
        if iTY_Char > 2:
            NH_Ht = float(NutHd_Ht)
            Nt_Thread_Ht = NH_Ht + Pit + Pit
            Subbodies = GetBodies(subComp1)
            if Subbodies:
                hide_body(Subbodies)                                # Hide the Bolt Threads
            OD1 = (float(MF_Gap) * 2.0)  + OD                   # Used if not doing real offsets of threads
            if ME_Units == 'M':
                BodyNut_Name = "M" + diameter + "_" + MF_Gap + "_MF_Gap_Nut"
            else:
                BodyNut_Name = Ediameter + "_" + Epitch + "TPIx" + EpitHelix + "HTPIx" + "_" + MF_Gap + "mm_MF_Gap_Nut"
            if RL_Check == 'Y':
                if iTY_Char == 3:
                    DrawThreads(subComp1, OD, Pit, PitHlx, F_Height, sPts, GR_Char, RL_Char, iST_Char, RL_Check, 1, iTY_Char)
                else:
                    DrawThreads(subComp1, OD, Pit, PitHlx, Nt_Thread_Ht, sPts, GR_Char, RL_Char, iST_Char, RL_Check, 1, iTY_Char)
            else:
                if iTY_Char == 3:
                    DrawThreads(subComp1, OD1, Pit, PitHlx, F_Height, sPts, GR_Char, RL_Char, iST_Char, RL_Check, 1, iTY_Char)
                else:
                    DrawThreads(subComp1, OD1, Pit, PitHlx, Nt_Thread_Ht, sPts, GR_Char, RL_Char, iST_Char, RL_Check, 1, iTY_Char)
            if iTY_Char > 3:
                DrawNut(subComp1, float(NutFlat_Dia), int(Nut_Sides), float(NutHd_Ht),float(pitch))
                subtract_bodies(subComp1)               # Subtract the Threads from the Nut
            if CN_Check == 'Y':
                if iTY_Char > 3:
                    ChamferNut(subComp1, OD1, Pit, PitHlx, NH_Ht, F_Cham_Wid, iTY_Char)
                else:
                    ChamferNut(subComp1, OD1, Pit, PitHlx, F_Height, F_Cham_Wid, iTY_Char)
            if Subbodies:
                unhide_body(Subbodies)              # Unhide the Bolt Threads
            bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
            numBodies = bsubComp1_bodies.count                  # Get a count of the bodies used, should be 3
            NutThreads = bsubComp1_bodies.item(numBodies-1)     # This should be the Nut just drawn
            NutThreads.name = BodyNut_Name                      # Rename the Nut or Nut Threads
# Group everything used to create the gear in the timeline.
    timelineGroups = design.timeline.timelineGroups
    TLend = design.timeline.markerPosition - 1
    timelineGroups.add(Tstart, TLend)
    end = time.time()
    Elapsed = round(end - start,2)
    #msg = f'Elapsed Time: {Elapsed} seconds'
    #ui.messageBox(msg)
def GetBodies(subComp1):
# Create an empty collection to store bodies
    bsubComp1_bodies = subComp1.bRepBodies              # Collect the bodies used in our component
    iBodies = bsubComp1_bodies.count
    all_bodies = adsk.core.ObjectCollection.create()
    if iBodies == 1:
        first_body = bsubComp1_bodies.item(0)
        all_bodies.add(first_body)
        return all_bodies
    elif iBodies > 1:
# Get all occurrences in the subcomponent
        occurrences = subComp1.occurrences
        for occurrence in occurrences:
# Get the component of the current occurrence
            component = occurrence.component
# Get all bodies in the component
            bodies = component.bRepBodies
            if bodies.count > 0:
# Add all bodies to the collection
                for body in bodies:
                    all_bodies.add(body)
        if all_bodies.count > 0:
            return all_bodies
        else:
            return False
    else:
        return False
def hide_body(Subbodies):
    if Subbodies.count == 1:
        Subbodies.item(0).isVisible = False
    else:
        for body in Subbodies:
            body.isVisible = False
def unhide_body(Subbodies):
    if Subbodies.count == 1:
        Subbodies.item(0).isVisible = True
    else:
        for body in Subbodies:
            body.isVisible = True
# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
# General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    #inputs = args.command.commandInputs
# These are all the inputs that are currently checked when they change in the dialog box
# MetTpe, diameter, pitch, angleTop, angleBot, Starts
# WhatType, height, pitHelix, splinePts, GuideRail, RightLeft, Cham_Wid, _ChamThread, _ChamNut, _RealOffset
# APITabBar, Bolt_Sides, BoltFlat_Dia, BoltHd_Ht, Nut_Sides, NutFlat_Dia, NutHd_Ht, MF_Gap
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    #msg = f'args.input.id = {args.input.id}'
    #ui.messageBox(msg)
    a_ID = args.input.id                    # Shorten name, since we test this a lot
    i_Calc = 0
    if a_ID == 'diameter' or a_ID == 'pitch' or a_ID == 'angleTop' or a_ID == 'angleBot' or a_ID =='Starts':
        i_Calc = 1
    if a_ID == "CSec_Type":
        #ui.messageBox('if a_ID == "CSec_Type":')
        I_Type = dropdownInput6.selectedItem.index
    # 1 Circle
    # 2 Polygon
    # 3 Ellipse
    # 4 Rectangle
    # 5 Star
        group_T3_1_input.isExpanded = False
        group_T3_2_input.isExpanded = False
        group_T3_3_input.isExpanded = False
        if I_Type < 3:
            group_T3_1_input.isExpanded = True      # Expand Circle, Ellipse & Polygon Group
        elif I_Type == 3:
            group_T3_2_input.isExpanded = True      # Expand Rectangle Group
        elif I_Type == 4:
            group_T3_3_input.isExpanded = True      # Expand Star Group
    if a_ID == 'WhatType':
        What_Id  = dropdown0CommandInput.selectedItem.index
        #ui.messageBox(f'What_ID = {What_Id}')
        if What_Id == 5:
            tabCmdInput3.activate()
    if a_ID == 'MetType':
        Met_ID = dropdownCommand_MInput.selectedItem.index
        Met_ID = Met_ID + 1

        diameter = Metdata[Met_ID][1]
        pitch = Metdata[Met_ID][2]
        BoltFlat_Dia = Metdata[Met_ID][3]
        BoltHd_Ht = Metdata[Met_ID][4]
        NutFlat_Dia = Metdata[Met_ID][3]
        NutHd_Ht = Metdata[Met_ID][5]
        Cham_Wid = Metdata[Met_ID][6]
        Thread_Wid = Metdata[Met_ID][7]
        Thread_Ht = Metdata[Met_ID][8]
#Metric, Diameter, Pitch, Hex Bolt Flat Diameter, Hex Head Thickness, Hex Nut Thickness, Chamfer Width, Thread Width
#M,      3,        0.5,   5.5,                    2.1,                2.4                0.4065         0.271
#0       1         2      3                       4                   5                  6              7
# Set all the appropriate text boxes
        _diameter.text = diameter
        _pitch.text = pitch
        _pitHelix.text = pitch                       # Decided to reset Helix Pitch to pitch when user changes Metric Thread Type
        _BoltFlat_Dia.text = BoltFlat_Dia
        _BoltHd_Ht.text = BoltHd_Ht
        _NutFlat_Dia.text = NutFlat_Dia
        _NutHd_Ht.text = NutHd_Ht
        _Cham_Wid.text = Cham_Wid
        _Thread_Wid.text = Thread_Wid
        _Thread_Ht.text = Thread_Ht
        i_Calc = 2
    elif a_ID == "EngType":
        Eng_ID = dropdownCommand_EInput.selectedItem.index
        Eng_ID = Eng_ID + 1

        Ediameter = Engdata[Eng_ID][1]
        Epitch = Engdata[Eng_ID][2]
        EpitHelix = Engdata[Eng_ID][2]
        BoltFlat_EDia = Engdata[Eng_ID][3]
        BoltHd_EHt = Engdata[Eng_ID][4]
        NutFlat_EDia = Engdata[Eng_ID][3]
        NutHd_EHt = Engdata[Eng_ID][5]
        Cham_Wid = Engdata[Eng_ID][6]
        Thread_Wid = Engdata[Eng_ID][7]
        Thread_Ht = Engdata[Eng_ID][8]
        _Ediameter.text = Ediameter
        _Epitch.text = Epitch
        _EpitHelix.text = EpitHelix
        _BoltFlat_EDia.text = BoltFlat_EDia
        _BoltHd_EHt.text = BoltHd_EHt
        _NutFlat_EDia.text = NutFlat_EDia
        _NutHd_EHt.text = NutHd_EHt
        _Cham_Wid.text = Cham_Wid
        _Thread_Wid.text = Thread_Wid
        _Thread_Ht.text = Thread_Ht
        i_Calc = 2
    elif a_ID == "EnglishMetric":
        EM_ID = dropdownInputEM.selectedItem.index      # 0 = English 1 = Metric
        if EM_ID == 0:
            group_E2input.isExpanded = True
            group_M2input.isExpanded = False
        else:
            group_E2input.isExpanded = False
            group_M2input.isExpanded = True
    elif args.input.id == 'Starts':
        IDX = dropdownInput3.selectedItem.index
        ReCalcHelixPitch(IDX)
# Only run this routine when we need to
    if i_Calc == 1:
        CalcThread(0)
# General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')
# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
# General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')
    inputs = args.inputs
# Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
# General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global local_handlers
    local_handlers = []