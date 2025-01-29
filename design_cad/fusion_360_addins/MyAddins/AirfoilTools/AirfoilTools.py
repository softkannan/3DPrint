# vim: set fileencoding=Windows-1252 :
#Author-Chris Drake
#Description-A comprehensive selection of utilities for creating, managing, and optimising\nairfoil shapes in air, water, or other gasses/fluids.  Contains tools to create\nWing surfaces, Cowling shapes, Propellers and Turbines, and utilities to read\nand write airfoil datafiles, to simplify and optimise file formats, to run\nparticle swarm optimisation on 2D airfoil shapes to maximise performance in your\nchosen situations, comparison solutions, spline sketch insertion, and more.
#Copyright-(C)2020 Chris Drake.  All rights reserved.  Note: This is NOT "Open Source": contact the author if you want to re-use any of this code.

VERSION=1.20200623                                                              # Remember to update this regularly!

# TODO
#   - preset save/load (next release)
#   - test things do not break when files are missing (settings, update, help)
#   - investigate converting from cubic B-splines to fusion control-point-splines https://www.autodesk.com/products/fusion-360/blog/sketch-control-point-splines-faq/?_ga=2.61932460.1487693074.1589630537-965653787.1589428597
#   - cache last manual input - it's annoying re-typing when doing repeats
#   - split foil def into its own reusable component
#   - add additional rotate and cyl-wrap-line inputs
#   - disc theory with units: https://web.mit.edu/16.unified/www/FALL/thermodynamics/notes/node86.html
#   - metadata: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-ED78D886-0B51-4FCA-98FA-A549EDEF7C04
#   - consider: https://forums.autodesk.com/t5/fusion-360-api-and-scripts/how-would-you-extract-expanded-points-from-a-spline/m-p/9567551#M10440
#   - investigate adsk.doEvents() to speed stuff up?

'''

evaluator = spline.geometry.evaluator
start, end = evaluator.getParameterExtents()
step = (end-start)/100

points = []
param= start
while param < end:
    points.append(evaluator.getPointAtParameter(param))
    param += step

'''


# Any thing or part that is exposed to moving gas or liquid can benefit from a streamlined shape.  In particular, wings, fins, ducts, propellers and turbines can all be vastly
# optimised by using the optimal correct shape.  "Optimal" is complicated; it depends on size, speed, turbulence, altitude (or depth), the properties of your medium (temperature 
# and density) and the surface finish you use (rough or smooth).  To further complicated things, many of those things are a range (e.g. speed, temperature, pressure, etc) and 
# when they are, there's often one point in that range where you need to concentrate on optimising (e.g. cruising speed at cruising altitude).  program_name/Airfoil Tools does this optimisation for you.

# RELEASE
# cd '/Users/cnd/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns'
# dozip; export ZFN=Airfoil_Tools-`now`_rel.zip; mv AirfoilTools/.vscode .;echo -e "Any thing or part that is exposed to moving gas or liquid can benefit from a streamlined shape.  In particular, wings, fins, ducts, propellers and turbines can all be vastly optimised by using the optimal correct shape." | zip -r $ZFN AirfoilTools/ -c -x 'AirfoilTools/airperl.pl' -x 'AirfoilTools/.DS_Store' -x 'AirfoilTools/.vscode/' -x 'AirfoilTools/resources/old/*';mv .vscode AirfoilTools/; unzip -t $ZFN |egrep '(DS_Store|vscode|airperl|old\b)'

import adsk.core, adsk.fusion, adsk.cam, traceback, math, os, subprocess, json, sys, select, socket, io, datetime, re, urllib.parse, time
from .foildb2020 import foildb2020
# import gettext, sqlite3, _thread
# from os import altsep



#################################################################################
####                                                                          ###
##                                Global defaults                              ##
####                                                                          ###
#################################################################################

(program_name,aft) = ('Airfoil Tools','_aft')                                   # Easy name-change (e.g. "Pro" version), and id suffix (e.g. '_aftpro') so (a) nothing clashes, and (b) we can run 2 at once, (c) can have different graphics (remember to update folder names!)

prog_folder= os.path.dirname(os.path.realpath(__file__))                        # We run companion programs from here, and some API calls require full path
settings_file = 'user_settings'+aft+'.json'                                     # Things like firstrun flag, units, history helpers, etc - see also home_file() for where this gets put
update_file = 'latest_version'+aft+'.json'                                      # Created async by check_update.py - contains JSON from website with current version data in it
resource_folder = '.' + os.sep + 'resources'                                    # Application.currentUser ?
abs_resource_folder = os.path.join(prog_folder,'resources')                     # clips cannot use relative folders :-()

panelorder = 0                                                                  # auto-increment ID so our dict has an order later
handlers = []                                                                   # global set of event handlers to keep them referenced for the duration of commands
mru={'mru':'','mruno':0}                                                        # Most-recently-used counter and pointer so we know the order they changed UI control in
(pnl,cmdh)=({},{})                                                              # All our panel control objects in one easy-to-get-to place
debug=False                                                                     # Might get toggled form the userdata later
(textpalette,textpalette_ori_state)=(None,False)                                # Gets set if the user wants to watch our commands/progress
units={'mps':{'scale':100},'m':{'scale':100},'C':{'offset':273.15}}             # How to convert to what I need from fusion numbers
_ui=None
pnl['loaded']=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
pnl['openc']=0


def main_aft():
    global uiel, userdata, updatedata, uiel_order, cmdl, pnl, debug, NEXTVERSION, clipa, clipb

    userdata=load_user_settings(settings_file)                                      # Get the users settings, defaults, preferences, presets, etc - empty if doesn't exist
    if not userdata:
        userdata={'debug':False,'release':True}                                     # Gets overwritten shortly by defaults in run() because 'firstrun' flag is missing here
    elif userdata.get("debug",0):
        debug=True

    updatedata=load_user_settings(update_file)                                      # Check any old previously-loaded update info. Gets re-populated when the user opens any dialogue
    if updatedata.get('fatal',0):                                                   # Note that this is "stale" info - the update data was fetched on a previous run; not this one.
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox(updatedata['fatal'])                                          # Unlikely - something so bad that continuing to run is a major problem, and no solution possible
        sys.exit(1)                                                                 # quit to prevent catastrophe (e.g. data corruption or security issue)
    NEXTVERSION='?'                                                                 # Gets updated to a next version string if an update is available
    if updatedata.get('loaded',0) and updatedata.get('current_version'+aft,0):
        NEXTVERSION='{:1.8f}'.format(updatedata['current_version'+aft])
    if userdata.get('applyupdate',0):                                               # Complete any file updates that might not have been applied earlier
        if updates(False):                                                          # Does the update
            userdata['applyupdate']=0
            save_user_settings(None,settings_file) 

    #eprint("Hello {}".format(__name__)) # Hello __main__%2FUsers%2Fcnd%2FLibrary%2FApplication%20Support%2FAutodesk%2FAutodesk%20Fusion%20360%2FAPI%2FAddIns%2FAirfoil%20Tools%2FAirfoil%20Tools_py



    #################################################################################
    ####                                                                          ###
    ##              Button and DropDown (slide-out) Menu Definitions.              ##
    ####                                                                          ###
    #################################################################################

    also='\n\nAlso inserts associated construction points and user-parameters (moments,' \
            'lift, drag, max L/D info, name, etc) useful for working with your new foil or shape.' # frequent static text

    # We create all our tooltip files at runtime, so all the doc is in this file instead of scattered around.     
    clipa='<!DOCTYPE html>\n<!-- CAUTION: auto-generated file. Do not change. (gets overwritten.) -->\n' \
        '<html><body BGCOLOR="#515151" WIDTH=300 TEXT="#ffffff" LINK="#ffffff" VLINK="#ffffff" ALINK="#ffffff" style="width:300">' \
        '<BASEFONT SIZE=3 FACE="Roboto,Arial,"Segoe UI","Helvetica Neue",sans-serif"><div style="color:white; width:300px;">' \
        '<table border=0 cellpadding=0 cellspacing=0 style="color:white; width:300px;"><tr><td width=298><b>'
    clipb='</b></tr></td></table></div></body></html>'
    infoa='<div style="color: #b5b5b5;">' # for showing derived values in the controls dialogue ui
    infob='</div>'

    # Put icons and clips into ./resources/[parentid]_[commandid_aft] (e.g ./solid_airfoil_command_aft_create_wing_aft/create_wing_aft.html). N.B. Uses *existence* of ['id'].html or .png to decide about using this folder.
    # if above missing, default:  ./resources/[commandid_aft]
    # if both missing, default: ./resources/
    uiel = {'airfoil_toolbar_button'+aft:
            { 'name':'Airfoils', # Button name - Fusion360 makes this AIRFOILS
                'type':'Button', 'ordr':nextId(),
                'desc':'Create, manage, and optimise airfoil shapes\nfor air, water, or other gasses/fluids.' +    # This text never shows anyplace - see about_help_command for what does show
                        '\n\n' + #             'info':
                        'Contains tools to create Wing surfaces, Struts, ' +
                        'Cowling shapes, Ducts, Propellers and Turbines.\n\n ' +
                        'Also has utilities to read and write airfoil datafiles; ' +
                        'to simplify, clean, repair, and optimise file formats; to run ' +
                        'particle swarm genetic optimisation (CFD) for ' +
                        'maximising performance for your specific need, '+
                        'performance analysis with charting and comparison '+
                        'tools, spline sketch insertion, comprehensive air/hydro '+
                        'foil library with precomputed ideal shapes, foil input '+
                        'scanning from photographs, calculators for Reynolds '+
                        'Numbers, fluid viscosity, power, torque, etc; and more.'},

        'solid_airfoil_command'+aft: # key is also the ID                        # all our user interface elements are in here
            { 'name':'Airfoil', # program_name, # Airfoil Tools
                'type':'DropDown', 'ordr':nextId(),
                'after':['PrimitivePipe'],                                         # Where on the menu to place our button after
                'desc':'Creates a solid airfoil, strut, cowling, duct propeller, or turbine.\n\n' +                # This text never shows anyplace - see about_help_command for what does show
                        'Select points or a path to locate your shape, and then ' + # Fusion360 auto-wraps these OK
                        'specify your expected operating conditions to ' +
                        'insert an ideal stream-lined foil (lofted spline) that is ' +
                        'CFD-Optimised to your need.'+also },

        'sketch_airfoil_command'+aft:
            { 'name':'Airfoil', # program_name, # Airfoil Tools
                'type':'DropDown', 'ordr':nextId(),
                'after':['DrawPoint'],                                             # Where on the menu to place our button after
                'desc':'Inserts airfoil points with a spline into the active sketch.\n\n' +                        # This text never shows anyplace - see about_help_command for what does show
                        'Select a chord line or nose and tail points, and ' +
                        'then specify your expected operating conditions.\n\n '+
                        'Can insert 2D or 3D sketch geometry.'+also },


        # Above are top-level controls.  Below is what goes into the above
        'about_help_command'+aft:                                                # This is the first menu item, because it is the one which has it's icon and text promoted to the parent control (airfoil button etc)
            { 'name':'Use the drop-down menu to insert foils in a new sketch', # 'About '+program_name+' + help/videos',
                'name.SketchCreatePanel':'About '+program_name+' + help/videos',
                'name.SolidCreatePanel':'About '+program_name+' + help/videos',
                'type':'Command', 'ordr':nextId(),
                #'tip':'Use the drop-down to open the sub-menu',

                'desc':'<hr><p>This Add-on lets you create, manage, and optimise airfoil shapes for air, water, or other gasses/fluids.</p>' + 
                        '<p>It contains tools to create Foil sketch profiles, Wing surfaces, Struts, ' +
                        'Cowling shapes, Ducts, Propellers and Turbines.</p>' +
                        '<p>It also has utilities to read and write airfoil datafiles; ' +
                        'to simplify, clean, repair, and optimise file formats; to run ' +
                        'particle swarm genetic optimisation (CFD) for ' +
                        'maximising performance for your specific need, '+
                        'performance analysis with charting and comparison '+
                        'tools, spline sketch insertion, comprehensive air/hydro '+
                        'foil library with precomputed ideal shapes, foil input '+
                        'scanning from photographs, calculators for Reynolds '+
                        'Numbers, fluid viscosity, power, torque, etc; and more.</p>',

                'desc.SolidCreatePanel':'Creates a solid airfoil, strut, cowling, duct propeller, or turbine.\n\n' +                # This text never shows anyplace - see about_help_command for what does show
                        'Select points or a path to locate your shape, and then ' + # Fusion360 auto-wraps these OK
                        'specify your expected operating conditions to ' +
                        'insert an ideal stream-lined foil (lofted spline) that is ' +
                        'CFD-Optimised to your need.'+also,

                'desc.SketchCreatePanel':'Inserts airfoil points with a spline into the active sketch.\n\n' +                        # This text never shows anyplace - see about_help_command for what does show
                        'Select a chord line or nose and tail points, and ' +
                        'then specify your expected operating conditions.'+also,

                'html':'<br><img src=../foilsep.png><br><p>' + 
                        program_name+' is written and maintained by:</p><p>'+
                        '<center>Chris Drake</center></p><p>' +
                        'Run this command to access our list of help topics and view '+
                        'quick introductory videos.</p>' ,
                'controls':[ 'banner', 'update_now', 'helpbanner' ] },


        'separator_1'+aft:{'ordr':nextId(), 'type':'Separator' },                # visually separate logically distinct commands

        'create_wing'+aft:
            { 'name':'Create Wing',
                'name.SketchCreatePanel':'Wingt',          # Alternate name to use if the parent is SketchCreatePanel
                'name.sketch_airfoil_command'+aft:'Wing',  # Alternate name to use if the parent is this
                'type':'Command', 'ordr':nextId(),
                #'desc.SketchCreatePanel':'Creates a Wing (lifting airfoil)\n\n' +
                'desc':'Creates a Wing (lifting airfoil)\n\n' +
                        'Select:-\n\n' +
                        '*  The Nose point (leading edge) of the foil\n' +
                        '*  Tail point (trailing edge)\n'+
                        '     these make the chord length\n' +
                        '+  Optional Join point - to insert foil\n'+
                        '     pre-rotated to best L/D AoA\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, and operating ' +
                        'conditions to insert the optimum foil shape for your purpose.\n\n'+
                        # '* Tip: See also the Mass and Span option below\n\n' +
                        # 'Tip: If you select only the Nose or Tail (not both), you can then specify ' +
                        # 'a span and load or weight instead, and ' + program_name + ' will work out ' +
                        # 'the best chord length for you.\n\n' + 
                        'Tip: A good Join Point is usually 25% in from the nose, which is very close ' +
                        'to the foil center of pressure.  Your foil will be auto-rotated by the best ' +
                        'angle of attack (AoA, or alpha) for the most efficient lift-to-drag (L/D) ' +
                        'condition matching your specifications.\n\n' +
                        'Tip: select the chord line to auto-rotate the foil about its center-of-pressure moment.',
                'desc.SolidCreatePanel':'Creates a:\n\n        *  Solid Wing (lifting airfoil)\nor    * Strut (low-drag symmetric foil).\n\n' + # placeholder reminder how to do different desc/images for different panels
                        'Select one of:-\n\n' +
                        '*  Chord line, forward direction, and width\n' +
                        '*  Nose and Tail points, and width\n' +
                        '*  Path and forward direction\n' +
                        '+ Optional moment center\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, and operating ' +
                        'conditions to insert the optimum foil shape for your purpose.',
                'res':['SketchCreatePanel','SolidCreatePanel'], # gets overwritten below - this tells our loader that this item has its own resource folder
                'html':'<center><img src=../create_wing_aft.png></center><br>'+also,
                'html.SolidCreatePanel':'<img src=../../foilsep.png><br>'+also,
                'html.SketchCreatePanel':'<center><img src=../../create_wing_aft.png></center><br>'+also,
                # 'controls':[ 'banner', 'update_now', 'nickname', 'wingorstrut', 'nose', 'tail', 'chord_info', 'join', 'preset', 
                'controls':[ 'banner', 'update_now', 'nickname', 'up', 'nose', 'tail', 'chord_info', 'join', 'preset', 
                            'medium_group', 'medium', 'density', 'dynamic_viscosity', 'kinematic_viscosity', 'turbulence', 'finish', 're_info', 

                            # 'velocity_group', 'targetspeed', 
                            # 'altitude_group', 'targetaltitude', 
                            # 'temperature_group', 'targettemperature', 

                            'velocity_group', 'minspeed', 'targetspeed', 'maxspeed', 
                            'altitude_group', 'minaltitude', 'targetaltitude', 'maxaltitude', 
                            'temperature_group', 'mintemperature', 'targettemperature', 'maxtemperature',
                            # 'mass_and_span_group', 'min_mass', 'target_mass', 'max_mass', 'target_span',
                            'settings_group', 'constrain', 'endcap', 'enddist', 'share' ] }, # 'save_preset_group', 'save', 'log', 

        'create_strut'+aft:
            { 'name':'Create Strut',
                'name.SketchCreatePanel':'Strut', # Alternate name to use if the parent is SketchCreatePanel
                'name.sketch_airfoil_command'+aft:'Strut', # Alternate name to use if the parent is this
                'type':'Command', 'ordr':nextId(),
                'desc.SketchCreatePanel':'Creates a strut (low-drag symmetric foil).\n\n' +
                        'Select:-\n\n' +
                        '*  The Nose point (leading edge) of the foil\n' +
                        '*  Tail point (trailing edge)\n'+
                        '     these make the chord length\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, and operating ' +
                        'conditions to insert the optimum foil shape for your purpose.',
                'desc':'Creates a strut (low-drag symmetric foil).\n\n' +
                        'Select one of:-\n\n' +
                        '*  Chord line, forward direction, and width\n' +
                        '*  Nose and Tail points, and width\n' +
                        '*  Path and forward direction\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, and operating ' +
                        'conditions to insert the lowest-drag foil shape for your purpose.',
                'res':['SketchCreatePanel','SolidCreatePanel'], # gets overwritten below - this tells our loader that this item has its own resource folder
                'html':'<center><img src=../create_strut_aft.png></center><br>' + also,
                'html.SolidCreatePanel':'<center><img src=../../create_strut_aft.png></center><br>' +also,
                'html.SketchCreatePanel':'<center><img src=../../create_strut_aft.png></center><br>'+also,
                'controls':[ 'banner', 'update_now', 'nickname', 'nose', 'tail', 'chord_info',  'preset', 
                            'medium_group', 'medium', 'density', 'dynamic_viscosity', 'kinematic_viscosity', 'turbulence', 'finish', 're_info', 
                            'velocity_group', 'minspeed', 'targetspeed', 'maxspeed', 
                            'altitude_group', 'minaltitude', 'targetaltitude', 'maxaltitude', 
                            'temperature_group', 'mintemperature', 'targettemperature', 'maxtemperature',
                            'settings_group', 'constrain', 'share' ] }, # 'save_preset_group', 'save', 'log', 

        'create_cowling'+aft:
            { 'name':'Create Cowling',
                'name.sketch_airfoil_command'+aft:'Cowling',
                'type':'Command', 'ordr':nextId(),
                'desc':'Creates a solid cowling (low-drag streamline shape)\n\n' +
                        'Select one of:-\n\n' +
                        '*  Chord line, forward direction, and thickness\n' +
                        '*  Nose and Tail points, and thickness\n' +
                        '+ Optional width for non-circular shrouds\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, and operating '+
                        'conditions to insert an optimum low-drag 3D shape for your purpose.',
                'html':'<center><img src=../create_cowling_aft.png></center><br>'+also,
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'create_duct'+aft:
            { 'name':'Create Airfoil Duct',
                'name.sketch_airfoil_command'+aft:'Duct',
                'type':'Command', 'ordr':nextId(),
                'desc':'Creates a Duct suitable for use as a propeller or turbine shroud.\n\n' +
                        'Select:-\n\n' +
                        '*  Center Chord line, forward direction,\n'+
                        '    and inner diameter\n' +
                        '*  Center Nose and Tail points, and\n'+
                        '    inner diameter\n' +
                        '+ Optional thickness constraint or outer\n'+
                        '    diameter\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, ' +
                        'propeller or turbine power, specifications, and operating '+
                        'conditions to insert an optimal duct for your purpose.',
                'html':'<center><img src=../create_duct_aft.png></center><br>'+also,
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'create_propeller'+aft:
            { 'name':'Create Propeller',
                'name.sketch_airfoil_command'+aft:'Propeller',
                'type':'Command', 'ordr':nextId(),
                'desc':'Creates a Driven Propeller.\n\n' +
                        'Select:-\n\n' +
                        '       *  Center Chord line, forward direction\n' +
                        'or   *  Center Nose and Tail points\n\n' +
                        'Next specify one of:-\n\n' +
                        '*  Power input available or output required\n' +
                        '*  Blade count and length or diameter\n' +
                        '+ Optional RPM range\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, ' +
                        'material and medium specifications, and operating '+
                        'conditions to insert optimal blade shape for your purpose.',
                'html':'<center><img src=../create_propeller_aft.png></center><br>'+also,
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'create_turbine'+aft:
            { 'name':'Create Turbine',
                'name.sketch_airfoil_command'+aft:'Turbine',
                'type':'Command', 'ordr':nextId(),
                'desc':'Creates a Driving Turbine.\n\n' +
                        'Select:-\n' +
                        '       *  Center Chord line\n' +
                        '       *  Nose point (flow entry point = direction)\n' +
                        '       *  Hub edge join point\n\n' +
                        'Next specify one of:-\n\n' +
                        '       * Power input available or output required\n' +
                        '       * Blade count and length or diameter or tip location\n' +
                        '       +  Optional RPM range\n\n' +
                        'Then specify your medium (air, water, etc), velocity range, ' +
                        'material and medium specifications, and operating '+
                        'conditions to insert the optimal blade shape for your purpose.',
                'html':'<center><img src=../create_propeller_aft.png></center><br>'+also,
                'controls':[ 'banner', 'update_now', 'nickname', 'centerline', 'hub_nose', 'root_chord_info', 'hub_edge', 'preset', # direction (anti-)clockwise
                            'medium_group', 'medium', 'density', 'dynamic_viscosity', 'kinematic_viscosity', 'turbulence', 'finish', # 're_info', 
                            # 'velocity_group', 'targetspeed', 
                            # 'altitude_group', 'targetaltitude', 
                            # 'temperature_group', 'targettemperature', 
                            'velocity_group', 'minspeed', 'targetspeed', 'maxspeed', 
                            'altitude_group', 'minaltitude', 'targetaltitude', 'maxaltitude', 
                            'temperature_group', 'mintemperature', 'targettemperature', 'maxtemperature',
                            # 'mass_and_span_group', 'min_mass', 'target_mass', 'max_mass', 'target_span',
                            'settings_group', 'share' ] }, # 'save_preset_group', 'save', 'log', 

        'separator_2'+aft:{'ordr':nextId(), 'type':'Separator' },               # visually separate logicily distinct commands

        'import_export'+aft:
            { 'name':'Import / Export airfoil data files',
                'type':'Command', 'ordr':nextId(),
                'desc':'Intelligently loads any kind of airfoil data file.\n' +
                        'Exports generated and/or inbuilt library airfoils to text data files in Selig format.\n' +
                        'Insert airfoils into sketch with attached spline.\n' +
                        'Loads and saves foils and favorites into your personal library.',
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'foil_maintenance'+aft:
            { 'name':'Airfoil data maintenance operations', #  [declutter] [normalize] [scale] [close] [spline/points-only] [compare] => can be sideways arrows in menus
                'type':'Command', 'ordr':nextId(), # Better as a DropDown ?
                'desc':'Offers a variety of processing operations on airfoil data\n\n' +
                        '*  Full Tidy: all the below\n\n' +
                        '*  Test: Detect data problems, like excessive angles, holes, duplicates, crossovers, etc\n\n' +
                        '*  Declutter: remove extraneous polar coordinate\n\n' +
                        '*  Normalize: make the front point the nose at (0,0) and the tail (1,0)\n\n' +
                        '*  Scale: Shrink or grow, symmetrically or asymmetrically\n\n' +
                        '*  Rotate: Change the angle of the airfoil data polar coordinates\n\n' +
                        '*  Close: join up any data holes (common at trailing ends)\n\n' +
                        'These utilities are for "foil geeks" only.  It is better to use foils '+
                        'suggested by '+program_name+' because ' +
                        'most 3rd party shapes are extremely inefficient (e.g. our foils outperform all NACA shapes by 57% to 120%)',
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'foil_performance'+aft:
            { 'name':'Airfoil performance analysis', # compare
                'type':'Command', 'ordr':nextId(),
                'desc':'Produce polar diagrams, Lift and Drag coefficients, moments, ' +
                        'and more for your chosen range of operating conditions.\n\n'+
                        'Compare multiple different airfoils from our database, '+
                        'your projects, or your personal library.\n\n'+
                        'Can insert results as user parameters and sketch images to '+
                        'easily share with others',
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'foil_optimize'+aft:
            { 'name':'Airfoil CFD genetic optimiser',
                'type':'Command', 'ordr':nextId(),
                'desc':'Specify the ranges of all operating conditions along with your weighting '+
                        'criteria to automatically generate the perfect shape to exactly suit your needs.\n\n' +
                        'Run on your own high-performance machine(s) to see results in a week, or distribute ' +
                        'your workload in the cloud to get faster answers.\n\n'+
                        program_name+' already includes pre-computed foils for many conditions, '+
                        'which typically outperform common shapes by 50% or more.  Use '+
                        'our genetic optimiser to get even better results',
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },

        'reynolds_calculator'+aft:
            { 'name':'Reynolds (Re) Number and Power Calculators',
                'type':'Command', 'ordr':nextId(),
                'desc':'Intelligent tool for working with the numbers that make ideal foils possible.\n\n'+
                        'Can load and save named inputs as favorites to help make your subsequent use of foils easier',
                'controls':[ 'banner', 'update_now', 'votebanner', 'votebox' ] },


        'separator_3'+aft:{'ordr':nextId(), 'type':'Separator' },               # visually separate logicily distinct commands

        'foil_bugs_and_requests'+aft:
            { 'name':'Report Bug / Request Feature',
                'type':'Command', 'ordr':nextId(),
                'desc':program_name + ' is under continual development.  It began in 2012 for high-performance ultralight propellers, and has morphed into a powerful suite of tools ' +
                    "for almost anything you can use a foil shape for.\n\n" +
                    "This Fusion360-edition is our first User-Interface to our existing code base, which contains vastly more features than we have so-far exposed in our UI.\n\n"+
                    "If you've found something that doesn't look right, or reached a UI command that we have not yet connected to our code base, or you have a request for a new feature "+
                    "you would like to see, please get in touch!\n\nRun this command to contact the author: Chris Drake.\n\n",
                'controls':[ 'banner', 'update_now', 'bugbanner' ] },
    #              'desc':"\n\nComing Shortly!  This command exists in our CLI tools package installed with this add-in, but we are still working on plumbing it's goodness into the Fusion360 UI.\n\n" +
    #                    "Use our feature-request option if you'd like us to prioritize something specific, or sit back and wait a few weeks for us to join all the dots, then check for an update!\n\n",


        'end'+aft: {'type':'end','ordr':0}  # add above here
        }



    #################################################################################
    ####                                                                          ###
    ##                     Dialogue box controls Definitions.                      ##
    ####                                                                          ###
    #################################################################################
    if sys.platform.startswith('darwin'): blueline= '<img src="'+  os.path.join(abs_resource_folder,'blueline3.png') +'" height=3>' # Mac irritatingly is 3 pixels higher...
    else: blueline= '<img src="'+  os.path.join(abs_resource_folder,'blueline.png') +'" height=1>'

    cmdl=[{'id':'banner'+aft,   # This gets overwritten by update messages, if any.   WARNING - must be first in list (see update code which grabs cmdl[0]['dflt'])
        'name':'',
        'type':'TextBoxCommandInput',
        'dflt':'<img border=0 align=left valign=top height=45 src="'+  os.path.join(abs_resource_folder,'banner_aft45.png') +'">' +
               '<b> &nbsp; &nbsp; &nbsp; &nbsp; <font size=+1>'+program_name+'</font></b>&nbsp;&nbsp;&nbsp;'+
               '<br> &nbsp; &nbsp; &nbsp; &nbsp; <font size=-1>v{:1.8f}'.format(VERSION) + ' ' + foildb2020.VERSION(VERSION) + '</font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
               '<br> &nbsp; &nbsp; &nbsp; <a href="http://ChrisDrake.com/Airfoil_Tools/">instructions</a> &nbsp; '+
               '<a href="https://forums.autodesk.com/t5/fusion-360-api-and-scripts/add-in-announcement-hydrofoil-and-airfoil-tools-seeking-your/td-p/9453985">forum</a><br>'+ blueline,

# Mac and Windows behave differently (url() does not work on windows, tables are broken, etc)
    #works    'dflt':'<div align="center"><img src="'+  os.path.dirname(os.path.realpath(__file__)) + "/resources/" + 'banner.png">'+program_name+' v<b>'+str(VERSION)+'<br><img src=resources/banner.png></b><a href="http:fusion360.autodesk.com">html.</a></div>',
    #works    'dflt':'<div align="center"><img src="'+  abs_resource_folder + '/banner.png">'+program_name+' v<b>'+str(VERSION)+'</b><a href="http:fusion360.autodesk.com">html.</a></div>',
    #OK!    'dflt':'<div align="center" style="overflow: visible;"><img src="'+  abs_resource_folder + '/banner.png" width=207 border=0 height=43></div>', # 207 ok 208 ng  43ok 44ng
#        'dflt':'<table border=0 cellpadding=0 cellspacing=0><tr><td rowspan=2><img src="'+  os.path.join(abs_resource_folder,'banner_aft.png') +'"></td><td align=right>' +
#               '<b><font size=+1>'+program_name+'</font></b>&nbsp;&nbsp;&nbsp;'+
#               '<br><font size=-1>v{:1.8f}'.format(VERSION) + ' ' + foildb2020.VERSION(VERSION) + '</font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
#               '<br><a href="http://ChrisDrake.com/Airfoil_Tools/">instructions</a> &nbsp; <a href="https://forums.autodesk.com/t5/fusion-360-api-and-scripts/add-in-announcement-hydrofoil-and-airfoil-tools-seeking-your/td-p/9453985">forum</a>'+
#               '</td></tr><td height=1px style="height:1px" bgcolor="#0091e2"></td></tr></table>', # 207 ok 208 ng  43ok 44ng
#                '<div align="right" style="overflow: visible; background-image: url('+  os.path.join(abs_resource_folder,'banner.png') +'); background-repeat: no-repeat;"><b>'+
#                '<b><font size=+1>'+program_name+'</font></b>&nbsp;&nbsp;&nbsp;'+
#                '<br><font size=-1>v{:1.8f}'.format(VERSION) + ' ' + foildb2020.VERSION(VERSION) + '</font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
#                '<br><a href="http://ChrisDrake.com/Airfoil_Tools/">instructions</a> &nbsp; <a href="https://forums.autodesk.com/t5/fusion-360-api-and-scripts/add-in-announcement-hydrofoil-and-airfoil-tools-seeking-your/td-p/9453985">forum</a>'+
#                '</div>', # 207 ok 208 ng  43ok 44ng
        'last':0},

        { 'id':'update_now'+aft,
        'name':'Update Now?',
        'type':'BoolValueInput',
        'invisible':True, # Hides it
        'desc':'An update to ' +program_name + ' is waiting to be installed.',
        'tip':'Check this box to update ' + program_name + ' to version ' + NEXTVERSION},
        #'tip':'Check this box to update ' + program_name + ' to the next version.'},

        {'id':'helpbanner'+aft,
        'name':'', # full width
        'type':'TextBoxCommandInput',
        'dflt':'<div><p>'+ program_name+' &copy; Copyright 2020 <br>is written and maintained by</p>\n\n'+
            '<p>                              <center>Chris Drake</center></p>\n\n' +
            '<p>Use the links above to access our online help or contact Chris.</p><hr>'+
            '<p>' + program_name + ' is under continual development. &nbsp; It began in 2012 for high-performance '+
            'ultralight propellers, and has since become a powerful suite of tools ' +
            'for almost anything you can use a foil shape for.</p>\n\n' +
            '<p>This Fusion360-edition is our first User-Interface to our existing code base.  We are working to '+
            'bring you all the features it supports in this: our easy-to-use UI.</p><hr>'+
            '<p><b>Our inbuilt airfoil database:</b><br>We began with a huge collection of every public airfoil we could find online. '+
            'We next discarded all patented/copyright ones, and added every NACA 4-series permutation (and many 5-series).</p>'+
            '<p>We then ran 768 permutations of our solver (64 Re/12 N) on every one, as well as "gradient-descent squashing" on each (top and bottom surfaces individually).</p>'+
            '<p>We targeted Max CL/CD (or 1/CD for struts), weighted by normal distribution, across +/- 3degrees AoA for performance optimisation.</P>'+
            '<p>Finally, we took the top ten performers from each permutation we targeted, and ran genetic particle-swarm optimisation on those.</p>'+
            '<p>The foils we include here are the result of many years high-performance CPU processing, and <b>should</b> outperform anything else you can find online, usually by a large margin.</p>'+
            '<p>Our future cloud service will allow you to generate even more ideal foils suited to your exact usage and weighting criteria. </p></div>',
    #                   "If you've found something that doesn't look right, or reached a UI command that we have not yet connected to our code base, or you have a request for a new feature "+
    #                   "you would like to see, please get in touch!\n\nRun this command to contact the author: Chris Drake.\n\n</div>' ,",
        'rows':48,
        'last':0},

        {'id':'votebanner'+aft,
        'name':'', # full width
        'type':'TextBoxCommandInput',
        'dflt':'<div><p>Do you need this feature?</p>\n'+
            '<p>'+ program_name + ' is a Fusion-360 user-interface added to our existing Airfoil utility system.</p>' +
            '<p>All features in our menu options exist, but it takes a lot of effort to wrap a UI around them.</p>' +
            '<p>If you want us to prioritize completing the UI for this feature, please vote below.</p>'+
                '</div>', # 207 ok 208 ng  43ok 44ng
        'rows':12,
        'last':0},

        { 'id':'votebox'+aft,
        'name':'Vote?',
        'type':'BoolValueInput',
        'dflt':False,
        'desc':'We prioritize our development based on the number of votes each feature receives',
        'tip':'Check this box to vote for this feature.'},


        {'id':'bugbanner'+aft,
        'name':'', # full width
        'type':'TextBoxCommandInput',
        'dflt':'<div><p>Please use our forum link above to report bugs.</p>'+
            '<p>Remember to screen-shot any error boxes that popped up, and add them to your forum post to help us find and fix what went wrong.</p>'+
            '</div>', # 207 ok 208 ng  43ok 44ng
        'rows':7,
        'last':0},

        { 'id':'nickname'+aft,
        'name':'Nickname',
        'type':'StringValueInput',
        'tip':'(Optional) Give your foil a name',
        'desc':'If you name your foil, the name will become a prefix in user parameters for the characteristics of this foil.'+
    #V2            'plus your foil and settings can be saved as a preset, so you can quickly re-use your parameters again in future. '+
                '\n\nThe nickname must start with a letter, then contain letters, numbers, and _ (no spaces).',
        'html':'<img src=user_parms_aft.png>', # HTML: Gets wrapped in clipa and clipb
        'last':0},

        { 'id':'wingorstrut'+aft,
        'name':'Wing or Strut',
        'type':'ButtonRowCommandInput',
        'tip':'', # leave this out - it overrides the button tips if used: 'Do you want a Wing (lifting shape) or Strut (Symmetrical low-drag shape)',
        'desc':'*  Select Wing to insert a shape optimised for\n'+
                '    best lift with lowest drag ( Max Cl/Cd )\n'+
                '*  Select Strut to get a shape optimised for\n'+
                '    lowest drag ( Min Cd )',
        'buttons':[{'name':'Wing (lifting shape)','res':os.path.join(resource_folder,'wing')},{'name':'Strut (low-drag symmetrical shape)','res':os.path.join(resource_folder,'strut')}],
        'html':'<img src=foilsep.png><br>(screen-shot showing wing vs strut - coming here soon)',
        'last':0},

        { 'id':'up'+aft,
        'name':'Up',
        'type':'ButtonRowCommandInput',
        'tip':'', # leave this out - it overrides the button tips if used: 'Do you want a Wing (lifting shape) or Strut (Symmetrical low-drag shape)',
        'desc':'*  Select upright to insert a lifting shape\n'+
                '    like a wing\n',
    #            '*  Select downwards to insert a downforce\n'+
    #            '    shape like a spoiler',
        'dflt':0, # first button is 0
        'buttons':[{'name':'Produces lift (e.g. wing)','res':os.path.join(resource_folder,'wing')},{'name':'Produces down force (e.g. spoiler)','res':os.path.join(resource_folder,'inverted')}],
        'html':'<center><img src=up_aft.png></center><br>*  Select downwards to insert a downforce<br>\n'+
                ' &nbsp;    shape like a spoiler<br><center><img src=down_aft.png></center>',
        'last':0},

        { 'id':'nose'+aft,
        'name':'Nose point',
        'type':'SelectionInput',
        'filter':['ConstructionPoints','SketchPoints'],
        'tip':'Chose a point to set the front of your foil',
        'desc':'The Nose and Tail determine the size and direction of your foil.',
        'html':'<center><img src=create_wing_aft.png></center>',
        'crsr':'Select nose point', # The text in the tooltip shown next to the cursor.
        'lim':[1,1], # Required
        'last':0},

        { 'id':'hub_nose'+aft,
        'name':'Hub nose point',
        'type':'SelectionInput',
        'filter':['ConstructionPoints','SketchPoints'],
        'tip':'Chose a point to set the front of your foil',
        'desc':'The Hub nose points into the flow direction (it is the front of the turbine, which the flow comes towards).',
        'html':'<center><img src=turbine_nose_aft.png></center>',
        'crsr':'Select hub nose point', # The text in the tooltip shown next to the cursor.
        'lim':[1,1], # Required
        'last':0},

        { 'id':'tail'+aft,
        'name':'Tail point',
        'type':'SelectionInput',
        'filter':['ConstructionPoints','SketchPoints'],
        'tip':'Chose a point to set the trailing end of your foil',
        'desc':'The Nose and Tail determine the size and direction of your foil.',
        'html':'<center><img src=create_wing_aft.png></center>',
        'crsr':'Select tail point',
        'lim':[1,1], # Required
        'last':0},

        { 'id':'chord_info'+aft,
        'name':'Chord',
        'type':'TextBoxCommandInput',
        'dflt':infoa+'nose to tail = chord'+infob,
        'rows':1,
        'unit':'mm',
        'disabled':True,
        'last':0},

        { 'id':'root_chord_info'+aft,
        'name':'Root chord',
        'type':'TextBoxCommandInput',
        'dflt':infoa+'center line = chord'+infob,
        'rows':1,
        'unit':'mm',
        'disabled':True,
        'last':0},

        { 'id':'join'+aft,
        'name':'Join point',
        'type':'SelectionInput',
        'filter':['ConstructionPoints','ConstructionLines','SketchPoints','SketchLines','LinearEdges','JointOrigins'], 
        'tip':'(Optional, Recommended) Pick a point or \nline to locate where to insert your foil.',  # Future note: use nose..tail to work out line direction
    #     'tip':'Pick a point or to locate foil.',  # Future note: use nose..tail to work out line direction
        'desc':'The ideal Angle-of-Attack (AoA or alpha)\ndiffers depending on foil size and conditions.\nIf you select this point, '+
                'your foil will be\ninserted and rotated by the ideal AoA relative\nto the direction indicated by the Nose to the\nTail line.\n\n'+
                "Tip: you can select the nose-to-tail line itself if\nyou like - and if you do this, the foil will be\nrotated about it's "+
                "central moment (usually\nabout 25% in from the nose)",
        'html':'<center><img src=create_wing_aft.png></center>',
        'lim':[0,1], # Sets setSelectionLimits(min=0,max=1) to make this optional.
        'crsr':'Select moment-center join point or line',
        'last':0},

        { 'id':'centerline'+aft,
        'name':'Center line',
        'type':'SelectionInput',
        'filter':['ConstructionLines','SketchLines','LinearEdges'], 
        'tip':'Rotational center.  Pick a line to indicate where the turbine rotates around.',
        'desc':'Blade foil sections will be cylindrically wrapped around this line relative to their distance away from it.',
        'html':'<center><img src=turbine_centerline_aft.png></center>',
        'crsr':'Select center rotation line',
        'lim':[1,1], # Required
        'last':0},

        { 'id':'hub_edge'+aft,
        'name':'Hub edge',
        'type':'SelectionInput',
        #'filter':['ConstructionPoints','ConstructionLines','SketchPoints','SketchLines','LinearEdges','JointOrigins'], 
        'filter':['ConstructionPoints','SketchPoints'],
        'tip':'Pick a point away from the center line to define hub radius.', 
        'desc':'The blade root airfoil will be wrapped around and connected at the cylinder formed by the center line and this point.',
        'html':'<center><img src=turbine_edge_aft.png></center>',
        'crsr':'Select hub edge point', # Future; accept circles too
        'lim':[1,1], # Required
        'last':0},

        { 'id':'preset'+aft,   # #Quick-insert (medium;Air(alt+temp)/Water(sea/fresh/depth/temp)/other m2/s, chord, thick, speed (m,km,knots,mph,foot,etc) ,conditions(rough+turbulent, smoothe+laminar...)
        'name':'Preset',        # sea temp average = 16C Air temp =15C... set 16 for start?
        'type':'DropDownCommandInput',
        'choices':[#'Select a preset...',
                    #'', # divider between customer presets, and built-ins
    #V2                'Your foil: testfoil', # populate rest here
                    '', # divider between customer presets, and built-ins
                    'Small toy glider','Medium R/C plane', 'Fast jet toy', 'Ultralight aircraft', 'GA propeller plane', 'Business jet', 'Airliner', 'Fighter jet like', 'Slow hobby drone', 'Long range recon drone', 'Fast jet drone',
                    '', # divider between customer presets, and built-ins
                    'Fast car', 'Highway truck',
                    '', # divider between customer presets, and built-ins
                    'Hydrofoil surf board', 'Hydrofoil powerboat', 'Hydrofoil transporter',
                    '', # divider between customer presets, and built-ins
                    #'Wind Turbine', 'Model Turbine', 'Water Turbine', 
                    #'', # divider between customer presets, and built-ins
                    '(none) - fill in below'],
                    # Logically, the below should be merged with the above... but despite the duplication, doing it this way makes maintenance of these values easier...
        'values':{ 'Small toy glider'      :{'medium'+aft:0, 'turbulence'+aft:1, 'finish'+aft:0,  'minspeed'+aft:3,    'targetspeed'+aft:5,    'maxspeed'+aft:10,    'minaltitude'+aft:0, 'targetaltitude'+aft:20, 'maxaltitude'+aft:200,  'mintemperature'+aft:10, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:2, 'SKIP-target_mass'+aft:123 },
                    'Medium R/C plane'      :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:4,    'targetspeed'+aft:6,    'maxspeed'+aft:12,    'minaltitude'+aft:0, 'targetaltitude'+aft:20, 'maxaltitude'+aft:150,  'mintemperature'+aft:10, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:1, 'SKIP-target_mass'+aft:123 },
                    'Fast jet toy'          :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:5,    'targetspeed'+aft:27,   'maxspeed'+aft:40,    'minaltitude'+aft:0, 'targetaltitude'+aft:20, 'maxaltitude'+aft:200,  'mintemperature'+aft:10, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:0.5, 'SKIP-target_mass'+aft:123 },
                    'Ultralight aircraft'   :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:15,   'targetspeed'+aft:25,   'maxspeed'+aft:32,    'minaltitude'+aft:0, 'targetaltitude'+aft:300, 'maxaltitude'+aft:3000,  'mintemperature'+aft:5,  'targettemperature'+aft:12, 'maxtemperature'+aft:30,  'target_span'+aft:10, 'SKIP-target_mass'+aft:123 },
                    'GA propeller plane'    :{'medium'+aft:0, 'turbulence'+aft:1, 'finish'+aft:2,  'minspeed'+aft:31,   'targetspeed'+aft:130,  'maxspeed'+aft:140,   'minaltitude'+aft:0, 'targetaltitude'+aft:8534, 'maxaltitude'+aft:9144,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:13, 'SKIP-target_mass'+aft:123 }, # Piper M600
                    'Business jet'          :{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:3,  'minspeed'+aft:54,   'targetspeed'+aft:272,  'maxspeed'+aft:276,   'minaltitude'+aft:0, 'targetaltitude'+aft:10668, 'maxaltitude'+aft:15544,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:17, 'SKIP-target_mass'+aft:123 }, # Cessna Citation XLS
                    'Airliner'              :{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:3,  'minspeed'+aft:66,   'targetspeed'+aft:252, 'maxspeed'+aft:258,    'minaltitude'+aft:0, 'targetaltitude'+aft:10668, 'maxaltitude'+aft:15544,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:123, 'SKIP-target_mass'+aft:123 }, # 737
                    'Fighter jet like'      :{'medium'+aft:0, 'turbulence'+aft:1, 'finish'+aft:2,  'minspeed'+aft:50,   'targetspeed'+aft:272, 'maxspeed'+aft:276,    'minaltitude'+aft:0, 'targetaltitude'+aft:12000, 'maxaltitude'+aft:18200,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:123, 'SKIP-target_mass'+aft:123 }, 
                    'Slow hobby drone'      :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:0,    'targetspeed'+aft:5,    'maxspeed'+aft:20,    'minaltitude'+aft:0, 'targetaltitude'+aft:50,    'maxaltitude'+aft:1000,  'mintemperature'+aft:10, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:123, 'SKIP-target_mass'+aft:123 },
                    'Long range recon drone':{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:3,  'minspeed'+aft:31,   'targetspeed'+aft:130,  'maxspeed'+aft:136,   'minaltitude'+aft:0, 'targetaltitude'+aft:10000, 'maxaltitude'+aft:16000,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:123, 'SKIP-target_mass'+aft:123 },
                    'Fast jet drone'        :{'medium'+aft:0, 'turbulence'+aft:1, 'finish'+aft:1,  'minspeed'+aft:50,   'targetspeed'+aft:272,  'maxspeed'+aft:276,   'minaltitude'+aft:0, 'targetaltitude'+aft:10000, 'maxaltitude'+aft:16000,  'mintemperature'+aft:16, 'targettemperature'+aft:16, 'maxtemperature'+aft:16,  'target_span'+aft:123, 'SKIP-target_mass'+aft:123 },

                    'Highway truck'         :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:25,   'targetspeed'+aft:27,   'maxspeed'+aft:30,    'minaltitude'+aft:0, 'targetaltitude'+aft:750, 'maxaltitude'+aft:2000,  'mintemperature'+aft:5, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:2.5, 'SKIP-target_mass'+aft:123 },
                    'Fast car'              :{'medium'+aft:0, 'turbulence'+aft:2, 'finish'+aft:0,  'minspeed'+aft:30,   'targetspeed'+aft:45,   'maxspeed'+aft:60,    'minaltitude'+aft:0, 'targetaltitude'+aft:750, 'maxaltitude'+aft:2000,  'mintemperature'+aft:5, 'targettemperature'+aft:16, 'maxtemperature'+aft:26,  'target_span'+aft:1.8, 'SKIP-target_mass'+aft:123 },
                                                                                                                            #
                    'Hydrofoil surf board'  :{'medium'+aft:3, 'turbulence'+aft:1, 'finish'+aft:2,  'minspeed'+aft:4,    'targetspeed'+aft:7,    'maxspeed'+aft:15,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:0.8, 'SKIP-target_mass'+aft:123 },
                    'Hydrofoil powerboat'   :{'medium'+aft:1, 'turbulence'+aft:1, 'finish'+aft:1,  'minspeed'+aft:8,    'targetspeed'+aft:32,   'maxspeed'+aft:52,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:2, 'SKIP-target_mass'+aft:123 },
                    'Hydrofoil transporter' :{'medium'+aft:2, 'turbulence'+aft:0, 'finish'+aft:2,  'minspeed'+aft:6,    'targetspeed'+aft:17,   'maxspeed'+aft:20,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:5, 'SKIP-target_mass'+aft:123 },
                                                                                                                            #
                    #'Wind Turbine'          :{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:2,  'minspeed'+aft:6,    'targetspeed'+aft:17,   'maxspeed'+aft:20,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:5, 'SKIP-target_mass'+aft:123 },
                    #'Model Turbine'          :{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:2,  'minspeed'+aft:6,    'targetspeed'+aft:17,   'maxspeed'+aft:20,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:5, 'SKIP-target_mass'+aft:123 },
                    #'Water Turbine'          :{'medium'+aft:0, 'turbulence'+aft:0, 'finish'+aft:2,  'minspeed'+aft:6,    'targetspeed'+aft:17,   'maxspeed'+aft:20,    'minaltitude'+aft:0, 'targetaltitude'+aft:0, 'maxaltitude'+aft:0,  'mintemperature'+aft:5, 'targettemperature'+aft:12, 'maxtemperature'+aft:16,  'target_span'+aft:5, 'SKIP-target_mass'+aft:123 },

                    '(none) - fill in below':{} },
        'tip':'pick settings for common scenarios'},


        #----------------------------   Medium
        { 'id':'medium_group'+aft,
        'name':'Medium',
        'type':'GroupCommandInput',
        'tip':'Specify the medium your foil will be operating in'},

        { 'id':'medium'+aft,
        'name':'            ',
        'type':'RadioButtonGroupCommandInput',
        'choices':['Air','Fresh Water','Sea Water','Any Water','Other'],
        'tip':'Specify the medium your foil will be operating in'},

        { 'id':'density'+aft,          # Density
        'name':'Fluid density',
        'type':'StringValueInput',
        'disabled':True,
        'invisible':True,
        #'desc':'does this show when disabled?',
        'html':'kilograms per cubic metre (kg/m<sup>3</sup>)',
        'tip':'Density of the gas or fluid medium, in SI units'},

        { 'id':'dynamic_viscosity'+aft,
        'name':'Dynamic viscosity',    # Dynamic viscosity
        'type':'StringValueInput',
        'disabled':True,
        'invisible':True,
        #'desc':'does this show when disabled?',
        'html':'pascal-second (Pa.s), or equivalently kilogram per meter per second (kg.m?1.s?1).',
        'tip':'Dynamic viscosity of the gas or fluid medium, in SI units'},

        { 'id':'kinematic_viscosity'+aft,
        'name':'Kinematic viscosity',   # Kinematic viscosity
        'type':'StringValueInput',
        'disabled':True,
        'invisible':True,
        #'desc':'does this show when disabled?',
        'html':'square meters per second (m<sup>2</sup>/s)',
        'tip':'Kinematic viscosity of the gas or fluid medium, in SI units'},


        { 'id':'turbulence'+aft,       # Turbulence
        'name':'Flow conditions',
        'type':'RadioButtonGroupCommandInput',
        'choices':['Laminar and clean', 'Average', 'Turbulent and dirty'],  # these combined with finish to make NCRIT
        'tip':"Tip: Turbulent is a better choice if you are not sure (Foils optimised for clean flows perform badly in dirty ones.)"},


        { 'id':'finish'+aft,
        'name':'Smoothness',            # Finish.  turb+finish mapping:  ncrit = 3*finish + turb-1  # Yields 3 to 14. no. use ncrit=3*finish + turb-1 +(turb==3&&finish<4)-(turb==1&&finish>1); # gives: f1t1=n3 f1t2=n4 f2t1=n5 f1t3=n6 f2t2=n7 f3t1=n8 f2t3=n9 f3t2=n10 f4t1=n11 f3t3=n12 f4t2=n13 f4t3=n14
        'type':'DropDownCommandInput',
        'choices':[#'Select a surface finish...', '',
                    'Very rough',
                    'Average',
                    'Clean',
                    'Very smooth'],
        'tip':'Will the material you make your foil from have a rough and uneven surface, or a clean and smooth one?'},

        { 'id':'re_info'+aft,
        'name':'Re Target',
        'type':'TextBoxCommandInput',
        'dflt':infoa+'(computed)'+infob,
        'rows':1,
        'disabled':True},

        #----------------------------   Velocity
        { 'id':'velocity_group'+aft,
        'name':'Velocity Range',
        'type':'GroupCommandInput',
        'desc':'* The combination of fluid turbulence and foil surface finish combine to determine the "NCrit" - a factor which governs when flow-separation takes place, '+
            'and hence ultimate foil efficiency limits.  Picking these correctly makes a big difference to optimum performance.',
    #    'html':'HTML test...',
        'tip':'Specify the range of speeds you want to support, and an ideal target velocity (cruise speed)'},

    # UI makes FloatSliderCommandInput unusable right now (input boxes are too small to see the numbers, tab button crashes fusion)
    #            { 'id':'speedrange'+aft,
    #            'name':'Min .. Max',
    #            'type':'FloatSliderCommandInput',
    #            'unit':'mps',
    #            #'range':['0 mps','380 mps'],
    #            'range':[0,380],
    #          'tip':'How slow do you need this to still work at'},

        { 'id':'minspeed'+aft,
        'name':'Min',
        'type':'ValueInput',
        'dflt':'0.0 mps',
        'unit':'mps',
        'invisible':True,
        'desc':'Add one of these suffixes if you want to use different units:'+
            '\n\n* mps   meters per second'+
            '\n\n* fps   foot per second'+
            '\n\n* mph   miles per hour'+
            '\n\n* knots',
        'tip':'How slow do you need this to still work at'},

        { 'id':'targetspeed'+aft,
        'name':'Target',
        'type':'ValueInput',
        'dflt':'0.0 mps',
        'unit':'mps',
        'desc':'Add one of these suffixes if you want to use different units:'+
            '\n\n* mps   meters per second'+
            '\n\n* fps   foot per second'+
            '\n\n* mph   miles per hour'+
            '\n\n* knots',
        'tip':'What speed do you want to have optimal performance at'},

        { 'id':'maxspeed'+aft,
        'name':'Max',
        'type':'ValueInput',
        'dflt':'0.0 mps',
        'unit':'mps',
        'invisible':True,
        'desc':'Add one of these suffixes if you want to use different units:'+
            '\n\n* mps   meters per second'+
            '\n\n* fps   foot per second'+
            '\n\n* mph   miles per hour'+
            '\n\n* knots',
        'tip':'How fast do you realistically need to go'},


        #----------------------------   Altitude
        { 'id':'altitude_group'+aft,
        'name':'Altitude Range',
        'type':'GroupCommandInput',
        'tip':'Specify the range of heights or depths you want to support, and an ideal target (cruising altitude)'},

    #    { 'id':'altituderange'+aft,
    #    'name':'Min .. Max',
    #    'type':'FloatSliderCommandInput',
    #    'unit':'m',
    #    #'range':['-11000 m','30000 m'],
    #    'range':[-11000,30000], # deepest ocean, Mariana Trench, is 10994, highest flight, sr-71, is 27432 ... hmm... but maybe we should allow for highly compressed or near vacuum stuff?
    #     'tip':'How low and high do you need this to still work at'},

        { 'id':'minaltitude'+aft,
        'name':'Min',
        'type':'ValueInput',
        'dflt':'0.0 m',
        'unit':'m',
        'invisible':True,
        'desc':'Specify the range of heights or depths you want to support, and an ideal target (cruising altitude)\n\n'+
            'Add any distance suffix if you want to use different units (e.g. mm, cm, m, micron, in, ft, yd, mi, nauticalMile, mil)',
        'tip':'What is the lowest altitude or depth you need to support'},

        { 'id':'targetaltitude'+aft,
        'name':'Target',
        'type':'ValueInput',
        'dflt':'0.0 m',
        'unit':'m',
        'desc':'Add any distance suffix if you want to use different units (e.g. mm, cm, m, micron, in, ft, yd, mi, nauticalMile, mil)',
        'tip':'What height or depth do you want to have optimal performance at'},

        { 'id':'maxaltitude'+aft,
        'name':'Max',
        'type':'ValueInput',
        'dflt':'0.0 m',
        'unit':'m',
        'invisible':True,
        'desc':'Add any distance suffix if you want to use different units (e.g. mm, cm, m, micron, in, ft, yd, mi, nauticalMile, mil)',
        'tip':'What is the highest altitude or depth you need to support'},


        #----------------------------   Temperature
        { 'id':'temperature_group'+aft,
        'name':'Temperature Offset Range',
        'type':'GroupCommandInput',
        'tip':'Specify the range of temperature conditions you need.'},

    #    { 'id':'temperaturerange'+aft,
    #    'name':'Min .. Max',
    #    'type':'FloatSliderCommandInput',
    #    'unit':'C',
    #    #'range':['-273 C','1500 C'],
    #    'range':[0,1773.15],
    #     'tip':'How cold and hot do you need your foil to manage'},

        { 'id':'mintemperature'+aft,
        'name':'Min',
        'type':'ValueInput',
        'dflt':'16 C',
        'unit':'C',
        'invisible':True,
        'desc':'For sea level, use actual temperature. For high-altitude, this is an offset temperature\n\n'+
            'Add one of these suffixes if you want to use different units:'+
            '\n\n* C   Celsius'+
            '\n\n* F   Fahrenheit'+
            '\n\n* K   Kelvin'+
            '\n\n* R   Rankine',
        'tip':'What is the coldest temperature you need to support'},

        { 'id':'targettemperature'+aft,
        'name':'Target',
        'type':'ValueInput',
        'dflt':'16 C',
        'unit':'C',
        'desc':'Add one of these suffixes if you want to use different units:'+
            '\n\n* C   Celsius'+
            '\n\n* F   Fahrenheit'+
            '\n\n* K   Kelvin'+
            '\n\n* R   Rankine',
        'tip':'What is the operating temperature of your fluid that you want to have optimal performance at'},

        { 'id':'maxtemperature'+aft,
        'name':'Max',
        'type':'ValueInput',
        'dflt':'16 C',
        'unit':'C',
        'invisible':True,
        'desc':'Add one of these suffixes if you want to use different units:'+
            '\n\n* C   Celsius'+
            '\n\n* F   Fahrenheit'+
            '\n\n* K   Kelvin'+
            '\n\n* R   Rankine',
        'tip':'What is the hottest temperature you need to support'},


        #----------------------------   Mass and Span option
        { 'id':'mass_and_span_group'+aft,
        'name':'Mass and Span option',
        'type':'GroupCommandInput',
        'tip':'Fill in these settings to auto-generate an ideal chord length for your project.'},

    #    { 'id':'mass_and_span_range'+aft,
    #    'name':'Mass Min .. Max',
    #    'type':'FloatSliderCommandInput',
    #    'unit':'kg',
    #    'range':[0,35000000],       # Saturn 5 - heaviest flying thing
    #     'tip':'What is the empty and fully loaded weight range your foil needs to support'},

        { 'id':'min_mass'+aft,
        'name':'Min Mass',
        'type':'ValueInput',
        'dflt':'0.0 kg',
        'unit':'kg',
        'invisible':True,
        'html':'<img src=foilsep.png><br>(screen-shot showing how this works - coming here soon)',
        'desc':'Add any mass suffix if you want to use different units (e.g. g, kg, slug, lbmass, ouncemass, tonmass)',
        'tip':'What is the lightest weight your foil needs to support'},

        { 'id':'target_mass'+aft,
        'name':'Target Mass',
        'type':'ValueInput',
        'dflt':'0.0 kg',
        'unit':'kg',
        'desc':'Tip: Use this option instead of the Nose and Tail points to let '+program_name+
            ' pick the ideal chord length to give your solution optimal performance.\n\n'+
            'Add any mass suffix if you want to use different units (e.g. g, kg, slug, lbmass, ouncemass, tonmass)',
        'tip':'At what weight do you want to have optimal performance'},

        { 'id':'max_mass'+aft,
        'name':'Max Mass',
        'type':'ValueInput',
        'dflt':'0.0 kg',
        'unit':'kg',
        'invisible':True,
        'desc':'Add any mass suffix if you want to use different units (e.g. g, kg, slug, lbmass, ouncemass, tonmass)',
        'tip':'What is the maximum weight your foil needs to lift'},

        { 'id':'target_span'+aft,
        'name':'Wingspan',
        'type':'ValueInput',
        'dflt':'0.0 m',
        'unit':'m',
        'desc':'Add any distance suffix if you want to use different units (e.g. mm, cm, m, micron, in, ft, yd, mi, nauticalMile, mil)',
        'tip':'What wingspan do you want (longer usually performs better)'},

        #----------------------------   Settings
        { 'id':'settings_group'+aft,
        'name':'Settings',
        'type':'GroupCommandInput',
        'tip':''},

        { 'id':'constrain'+aft,
        'name':'Constrain',
        'type':'BoolValueInput',
        'dflt':False,
        'desc':'Your foil will be anchored to the join or nose point you selected.  If that point is parametric, and if you select this option, '+
            'your inserted foil will move properly if you change that point.\n\n'+
            'Tip: future '+program_name+' releases will include fully parametric foils: If you choose this option now, and if you give '+
            'your foil a nickname, your foils (in future) will re-compute and re-draw when:\n'+
            '* you change the chord (distance between nose and tail points) or\n'+
            '* you change any foil settings (e.g. the speed, in the user-parameters) or\n'+
            '* you install any update to '+program_name+' that includes new foil shapes that our solver has found to outperform the ones you inserted now.',
        'html':'<center><img align=left src=constrain_aft.png></center>',
        'tip':'Check this box to insert a fully-constrained shape.\n\nNOTE: Be patient - this takes 2+ minutes to insert.'},

        { 'id':'endcap'+aft,
        'name':'3d endcap',
        'type':'BoolValueInput',
        'dflt':False,
        'desc':'This creates ellipses from all the top-surface points to the corresponding under-surface points, through a mid-point that is 50% out from the edge.',
        'html':'<center><img src=round_side_aft.png></center>',
        'tip':'Insert rounded 3D "rib" end profiles suitable for lofting a tidy side to your foil.'+
            '\n\nNOTE: Be patient - this takes 1 minute to insert (or 5+ minutes if you also constrain).'},

        { 'id':'enddist'+aft,
        'name':'End distance %',
        'type':'ValueInput',
        'dflt':'100',
        'unit':'',
        'invisible':True,
        'html':'<table border=0>'+
            '<tr><td>100% is circular</td><td><img src=round_close.png></td></tr>'+
    #           '<tr><td colspan=2><img src=round_side.png></td></tr>'+
            '<tr><td>10% would be flat</td><td><img src=flat_close.png></td></tr>'+
    #           '<tr><td colspan=2><img src=flat_side.png></td></tr>'+
            '<tr><td>800% would be very pointy</td><td><img src=pointy_close.png></td></tr>'+
    #           '<tr><td colspan=2><img src=pointy_side.png></td></tr>',
            '</table>',
        'tip':'How rounded do you want the end?'},

        { 'id':'share'+aft,
        'name':'Share',
        'type':'BoolValueInput',
        'dflt':False,
        'desc':'Do not select this on test or junk foils, or on confidential projects.\n\n'+
            'This option sends us a copy of your settings from this panel.  We use this data to guide our solver so future '+program_name+
            ' updates will include foil shapes more perfectly suited to the requirements of you and our other users.\n\n'+
            'Optional: fill in the min+max settings above to help us plan our solver performance envelope settings.',
        'tip':'Share your foil settings with us.'},

        #----------------------------   Save
    #V2    { 'id':'save_preset_group'+aft,
    #V2    'name':'Save into presets',
    #V2    'type':'GroupCommandInput',
    #V2     'tip':''},

    #            { 'id':'test0'+aft,
    #            'name':'', # omit for full-wid
    #            'type':'TextBoxCommandInput',
    #            'dflt':"<html>hello <b>there</b> <input type=text name=test1 value='test1'>  <input type='submit' name='foo' value='foo' onclick='sendInfoToFusion()'>Click TO crash</input> ",
    #            'desc':'html testing desc',
    #            'html':'<img src=foilsep.png><br>this is a toolClip <b>HTLM</b> test string',
    #             'tip':'html tip test.'},

    #V2    { 'id':'test1'+aft,
    #V2    'name':'', # omit for full-wid
    #V2    'type':'ImageCommandInput',
    #V2    'dflt':resource_folder+'//foilsep.png'},

    #V2    { 'id':'save'+aft,
    #V2    'name':'Save',
    #V2    'type':'BoolValueInput',
    #V2    'dflt':True,
    #V2    'desc':'Tip: to remove a preset you saved earlier but no longer want, enter the Nickname of that preset and un-check this box.',
    #V2     'tip':'Check this box to save your settings into the Preset dropdown.'},

    # future featurecreep...
    #    { 'id':'log'+aft,
    #    'name':'Show log',
    #    'type':'BoolValueInput',
    #    'dflt':True,
    #    #'dflt':debug, # Default is false for normal users, true for me
    #     'tip':'Check this box to view the runtime log of ' + program_name},

        {'type':'end'}  # add above here
        ]



    #'Then specify your medium (air, water, etc), velocity range, and operating ' +
    #'conditions to insert the optimum foil shape for your purpose.\n\n'+
    #'Tip: If you select only the Nose or Tail (not both), you can then specify ' +
    #'a span and load or weight instead, and ' + program_name + ' will work out ' +
    #'the best chord length for you.\n\n' + 
    #'Tip: A good Join Point is usually 25% in from the nose, which is very close ' +


    #################################################################################
    ####                                                                          ###
    ##        Button, DropDown (slide-out), and dialogue-controls Expanders.       ##
    ####                                                                          ###
    #################################################################################

    # Populate uiel_order and uiel with additional keys that we need later
    uiel_order=[None]*(len(uiel))
    for i in uiel:                                                                  # Make a list, and put all our UI ID's into it in the correct order
        uiel_order[uiel[i]['ordr']]=i
        uiel[i]['id']=i                                                             # Store our id name in ourselves
        myres=resource_folder                                                       # use default if it doesn't have its own - See also aft_make_ui: per-toolbar ones override these
        if os.path.isdir(os.path.join(prog_folder, resource_folder, i)):             # Every control etc has its own set of icons, help, and Clip images
            myres=os.path.join(resource_folder, i)
            #eprint(myres)
        if uiel[i].get('res',0):                                                    # res - if it exists already, use it to create many sub res items...
            for subres in uiel[i]['res']:                                           # For every submenu... ('SolidCreatePanel',)
                useres=os.path.join(myres, subres)                                  # e.g. uiel[i]['res.SketchCreatePanel'] = './resources/create_wing_aft/SketchCreatePanel'
                abs_useres=os.path.join(prog_folder, useres)                        # clips cannot be relative :-()
                if os.path.isdir( abs_useres ):
                    uiel[i]['res.'+subres]=useres
                    uiel[i]['abs_res.'+subres]=os.path.join(prog_folder, useres)
                    #eprint("use:"+useres)
        uiel[i]['res']=myres                                                        # replace the temp list above with the default resource folder location
        uiel[i]['abs_res']=os.path.join(prog_folder, myres)
        (uiel[i]['ctrl'], uiel[i]['cmd'], uiel[i]['def'], uiel[i]['cb'])=({},{},{},{})  # Where we hold all our command objects; indexed by parentID (mywhere)
        if not uiel[i].get('name',0):
            uiel[i]['name']=i                                                       # Give separators a name, so debug output works OK
    if aft: # create aliases from ID-name (with prefix, to prevent toolbar naming collisions) back to base name (no prefix)
        for i in uiel_order:
            uiel[aft+i]=uiel[i]


    # Auto-populate anything missing from cmdl, to avoid key errors later
    for ctrl in cmdl:
        ctrl['abs_res']=abs_resource_folder
        for defaultible in ('dflt', 'tip', 'desc' ):                                # Things that must exist
            if ctrl.get(defaultible,'!!') =='!!': # some defaults can be zero
                ctrl[defaultible]=''
        if ctrl['type'] == 'TextBoxCommandInput' and not ctrl.get('rows',0):
            ctrl['rows']=3                                                          # Default to 3-rows for text lines
        if ctrl.get('id',0):
            cmdh[ctrl['id']]=ctrl                                                   # Create a dict pointing into the list


    

#################################################################################
####                                                                          ###
##                              Dialogue builder                               ##
####                                                                          ###
#################################################################################
#def aft_make_dlg(ui,aftid,mywhere,parentwhere,pctrl):                          # Build the popup dialogue box
def aft_make_dlg(cmd,pnlid):                                                    # Gets called from MyCommandCreatedEventHandler #cmd = args.command
    global cmdl, uiel, pnl, mru, NEXTVERSION

    dlg = cmd.commandInputs
    app = adsk.core.Application.get()
    ui  = app.userInterface
    panel=cmd.parentCommandDefinition.id

    #meta=dlg.addStringValueInput('meta'+aft,'Internal Settings', json.dumps( {'VERSION':VERSION, 'aft':aft, 'mywhere':self.mywhere, 'parentwhere':self.parentwhere, 'altid':self.altid} )) # In case later executions needs to know where this data came from...
    meta=dlg.addStringValueInput('meta'+aft,'Internal Settings', json.dumps( {'VERSION':VERSION, 'aft':aft} )) # In case later executions needs to know where this data came from...
    meta.isVisible=False
    panelname=dlg.addStringValueInput('panel'+aft,'Internal name of this dialog popup', pnlid['mywhere'] + '_' + pnlid['aftid'])    # So event handlers know what this data is (should we later remove pnlid from them)
    panelname.isVisible=False   # Added before I decided if I need this, so, might not be used...

    if updatedata.get('loaded',0) and updatedata.get('current_version'+aft,0):
        NEXTVERSION='{:1.8f}'.format(updatedata['current_version'+aft])
        eprint("most recent version is {}".format(NEXTVERSION))
        if not pnl.get('toldversion',0):
            vlog("most recent version is {}".format(NEXTVERSION))
            pnl['toldversion']=True
    else:
        msg=updatedata.get('error',0)
        eprint('{}: update check problem: {}'.format(program_name,msg))
        if not pnl.get('toldversion',0):
            vlog('{}: update check problem: {}'.format(program_name,msg))
            pnl['toldversion']=True

    # Build a list of the UI elements we want to have in this menu option
    docontrols={} # which controls we want to include
    ctrllist=[]   # controls order
    for ctrlname in uiel[pnlid['aftid']].get('controls',[]):
        if ctrlname:
            docontrols[ctrlname + aft]=True  # use the ones defined in the menu if it has them
            if cmdh.get(ctrlname+aft,0):
                ctrllist.append(cmdh[ctrlname+aft])
    if not len(docontrols):
        for ctrl in cmdl:
            if ctrl.get('id',0):
                docontrols[ctrl['id']]=True  # create a default set of all controls
                ctrllist.append(ctrl)


    mygroup=dlg
    if 1:   # Go through all possible input elements, and put the right ones for this use case into the dialogue
        #for ctrl in cmdl:
        for ctrl in ctrllist:
            if docontrols.get(ctrl.get('id',0),False): # is it one we want to include?
                # eprint("Doing " + ctrl['name'] + " of type "+ ctrl['type'])
                ctrlmethod=getattr(mygroup,'add'+ctrl['type']) # NB; GroupCommandInput differs  # all control methods start with "add"
                ctrlinstance=None

                if ctrl['type'] == 'StringValueInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],ctrl['dflt']) # (id, name, initialValue) # initialValue is optional
                    #ctrlinstance.isValueError = True # make it red

                elif ctrl['type'] == 'ValueInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],ctrl['unit'],adsk.core.ValueInput.createByString(ctrl['dflt'])) # (id, name, unitType, initialValue) # initialValue must be float (in base units) or suitable string

                elif ctrl['type'] == 'SelectionInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],ctrl['crsr']) # (id, name, commandPrompt) # commandPrompt is the text in the tooltip shown next to the cursor.
                    if ctrl.get('lim',0):
                        ctrlinstance.setSelectionLimits(ctrl['lim'][0],ctrl['lim'][1]) # (minimum, maximum) if 0, makes this optional
                    if ctrl.get('filter',0):
                        for filt in ctrl['filter']:
                            ctrlinstance.addSelectionFilter(filt)                   # ['ConstructionPoints','ConstructionLines','SketchPoints','SketchLines','LinearEdges','JointOrigins'] usually.

                elif ctrl['type'] == 'FloatSliderCommandInput':
                    ctrlinstance=ctrlmethod( ctrl['id'], ctrl['name'], ctrl['unit'], ctrl['range'][0] , ctrl['range'][1] , True) # (id, name, unitType, min, max, hasTwoSliders) # hasTwoSliders is optional
                    #ctrlinstance=ctrlmethod( ctrl['id'], ctrl['name'], ctrl['unit'], adsk.core.ValueInput.createByString( ctrl['range'][0] ), adsk.core.ValueInput.createByString( ctrl['range'][1] ), True) # Broken - too tired to work out why...

                elif ctrl['type'] == 'ButtonRowCommandInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],False) # (id, name, isMultiSelectEnabled)
                    didx=0
                    for but in ctrl['buttons']:
                        try:
                            ctrlinstance.listItems.add(but['name'],(ctrl.get('dflt','') !='' and ctrl.get('dflt',-1) == didx),but['res'])    # Caution - crashes dialog if these are missing
                        except:
                            eprint('panel button {} create fail'.format(but['name']))
                        didx=didx+1

                elif ctrl['type'] == 'RadioButtonGroupCommandInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name']) # (id, name) # name is optional
                    radio=ctrlinstance.listItems
                    for radioitem in ctrl['choices']:
                        radio.add(radioitem, False)

                elif ctrl['type'] == 'DropDownCommandInput':
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],adsk.core.DropDownStyles.TextListDropDownStyle) # (id, name, dropDownStyle); CheckBoxDropDownStyle/CheckBoxDropDownStyle/TextListDropDownStyle
                    radio=ctrlinstance.listItems
                    for radioitem in ctrl['choices']:
                        radio.add(radioitem, False, 'foo')

                elif ctrl['type'] == 'BoolValueInput':
                    if ctrl.get('dflt',0):
                        ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],True,'',ctrl['dflt']) # id, name, isCheckBox, resourceFolder, initialValue
                    else:
                        ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],True) # id, name, isCheckBox, resourceFolder, initialValue

                elif ctrl['type'] == 'GroupCommandInput':                                   # Future - mode the name of this to include "Air" or "Water" etc after they've picked one
                    #ui.messageBox( "thinking about " + ctrl['name'] + ":" + ctrl['type'] + " in " + self.aftid + " of " + self.mywhere)
                    ctrlmethod=getattr(dlg,'add'+ctrl['type'])  # put all groups in the parent
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name']) # (id, name)
                    ctrlinstance.isExpanded = True
                    ctrlinstance.isEnabledCheckBoxDisplayed = False
                    mygroup = ctrlinstance.children

                elif ctrl['type'] == 'TextBoxCommandInput':             # Can do full-width HTML (omit name to get full width)
                    text=ctrl['dflt']
                    if ctrl['id']=='banner'+aft and updatedata.get('update_msg',0):
                        text=updatedata['update_msg']                   # Tell user of any important updates when they open our panel
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],text,ctrl['rows'],True) # (id, name, formattedText, numRows, isReadOnly)

                elif ctrl['type'] == 'ImageCommandInput':             # Can do full-width HTML (omit name to get full width)
                    ctrlinstance=ctrlmethod(ctrl['id'],ctrl['name'],ctrl['dflt']) # (id, name, imageFile) # Example uses './/Resources//Fusion360Logo.png'


                if ctrlinstance:
                    if ctrl['tip']:
                        ctrlinstance.tooltip=ctrl['tip']   #"base tooltip string. This is always shown for commands."
                    if ctrl['desc']:
                        ctrlinstance.tooltipDescription=ctrl['desc']    #"If the tooltip description and/or tool clip are also specified then the tooltip will progressively display more information as the user hovers the mouse over the control."
                    if ctrl.get('disabled',0):
                        ctrlinstance.isEnabled=False
                    if ctrl.get('invisible',0):
                        ctrlinstance.isVisible=False

                    try:                                                        # keep a record of what we made as we make it.
                        if not pnl.get(panel,0):
                            (mru['mruno'], pnl[panel])=( mru['mruno']+1, {'mru':mru['mruno']})      # Create pnl[panel], and populate it with anyting for now - maybe mru will be handy later...
                        pnl[panel][ctrl['id']]=ctrlinstance                     # So our input handlers can easily find stuff...
                    except:
                        eprint("add_and_remember failed")

                    if 1:
                        try:
                            clipfn=make_html(pnlid['mywhere']+"."+pnlid['aftid']+"."+ctrl['id'],ctrl) # abs_resource_folder + 'airfoil_toolbar_button_aft.create_duct.nickname.html' 
                            if clipfn:
                                #eprint(clipfn)
                                ctrlinstance.toolClipFilename=clipfn
                        except:
                            eprint('ctrlinstance.toolClipFilename failed: {}'.format(traceback.format_exc()))

    return panel
        # We want the errors - hiding them is silly...
        #        except:
        #            if self.ui:
        #                self.ui.messageBox('Panel command created failed: {}'.format(traceback.format_exc()))





# 2.22, 2.32 in https://40p6zu91z1c3x7lz71846qd1-wpengine.netdna-ssl.com/wp-content/uploads/2017/02/Engineering-Fluid-Mechanics-9th-Edition-Crowe-Solution-Manual.pdf


#################################################################################
####                                                                          ###
##                           Validate - O - Rama                               ##
####                                                                          ###
#################################################################################

def MyValidate(pnlid,args,inputs,caller):
    global mru,pnl,userdata,textpalette,debug,updatedata,VERSION
    try:
        valid=0
        invalid={}
        if pnlid['aftid']=='create_strut'+aft or \
           pnlid['aftid']=='create_wing'+aft:
           invalid={'nickname':1, 'turbulence':1, 'finish':1, 'medium':1, 'chord':1, 're':1} # these get removed as we do them - when len(invalid)==0 we know we are good to go!
        if pnlid['aftid']=='create_turbine'+aft:
           invalid={'nickname':1, 'hub_radius':1, 'turbulence':1, 'finish':1, 'medium':1, 'targetspeed':1, 'targettemperature':1, 'root_chord_info':1, 'hub_edge':1, 'hub_nose':1} # these get removed as we do them - when len(invalid)==0 we know we are good to go! # 'targetaltitude':1,

        app = adsk.core.Application.get()
        ui = app.userInterface
        web_nbreq(None) # proccess any non-blocking operations

        dist=0

        panel=pnlid['mywhere'] + '_' + pnlid['aftid'] # 'sketch_airfoil_command_aft' + '_' + 'menuid':'create_cowling_aft'
        thisctrl=''
        if caller=='changed': # chgargs:
            (mru['mruno'], mru['mru'], mru[args.input.id])=( mru['mruno']+1, args.input.id, mru['mruno'])   # Update most-recently-used counter and pointers
            thisctrl=args.input.id  # e.g. nose_aft - Also has acccess to command.parentCommandDefinition.id  (same as pnlid mywhere+aftid)
        else:
            pass

        dlg=pnl[panel]

        # They want to update
        if thisctrl=='update_now'+aft:
            if dlg[thisctrl].value == True:   # They just checked the update checkbox
                if ui:
                    click=ui.messageBox('You are using {} version {:1.8f}.\nThe newest version is {}.\n\nYou will need to stop and re-start this add-in after you update.\n\nUpdate now?'.format(program_name,VERSION,NEXTVERSION),'Confirm update',adsk.core.MessageBoxButtonTypes.OKCancelButtonType) # messageBox(text, title, buttons, icon); OKCancelButtonType==1
                    if click==0: #ok
                        userdata['applyupdate']=1
                        save_user_settings(ui,settings_file) 
                        updates(False) # Does the update
                        dlg[thisctrl].isVisible=False # remove update box - done now.
                        if updatedata.get('update_msg',0):
                            updatedata['update_msg']=''                         # don't show the old update message after they updated
                            if updatedata.get('last_check_time',0): updatedata['last_check_time']= updatedata['last_check_time']-24*60*60 # force a re-check on next reload
                            save_other_settings(update_file,updatedata)         # don't show the old update message when they restart, and force a re-check
                        check_update(5) # Run a new update-check to see if there is anything else waiting (important if we just updated the updater)
                        ui.messageBox('Update complete.  To re-start '+program_name+':\n\n'+
                                      '* push Shift-S to open the Scripts-and-Add-Ins menu,\n'+
                                      '* Click the Add-Ins tab\n'+
                                      '* Click on '+program_name+
                                      '\n* Click Stop\n'+
                                      '* Click Run','Update complete')

                        try:
                            pnl[panel]['banner'+aft].formattedText = cmdl[0]['dflt'] # line 1067
                        except:
                            eprint("failed setting banner text back to default")

                        # Reset this so new dialogues don't say old stuff:
                        # text=updatedata['update_msg']   
                        # update the update json (and set last-check to 0 for next)?
                        # Re-run updater now

                        # Go fix any panels that already got built:-
                        #pnl[panel][ctrl['id']]=ctrlinstance 

                    else:
                        dlg[thisctrl].value=False # un-check the box because they cancelled


        # Delete unwanted presets
        if thisctrl=='save'+aft: # V2
            dlg['save_button_state'+aft]=dlg['save'+aft].value                      # Remember real value, so we can toggle this on errors without forgetting
            if dlg[thisctrl].value == False and len(dlg['nickname'+aft].value)>0:   # They just un-checked the save checkbox with a nickname entered
                if ui:
                    click=ui.messageBox('Delete saved pre-set "{}" - are you sure?'.format(dlg['nickname'+aft].value),'Confirm delete user preset',adsk.core.MessageBoxButtonTypes.OKCancelButtonType) # messageBox(text, title, buttons, icon); OKCancelButtonType==1
                    if click==0: #ok
                        pass  # remove etc here...


        # Prepare for sharing (reveal / hide range elements)
        if thisctrl=='share'+aft:
            showhide=[ 'minspeed', 'maxspeed', 'minaltitude', 'maxaltitude', 'mintemperature', 'maxtemperature' ] 
            if dlg[thisctrl].value:
                for ctrlname in showhide:
                    dlg[ctrlname+aft].isVisible=True
                web_nbreq('S={}&V={}&P={}'.format(int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()),VERSION,panel)) # non-blocking socket.
            else:
                for ctrlname in showhide:
                    dlg[ctrlname+aft].isVisible=False

        # Record a user vote for a feature
        if thisctrl=='votebox'+aft and dlg[thisctrl].value:
            web_nbreq('vote={}&now={}&V={}'.format(panel,int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()),VERSION)) # non-blocking socket.

        if dlg.get('votebox'+aft,0) and dlg['votebox'+aft].value:
            args.areInputsValid = True
            return True # enable OK if they checked the box (does nothing - we recorded their vote when they clicked it)

        # Reveal endap distance if they select it
        if thisctrl=='endcap'+aft:
            ctrlname = 'enddist'
            if dlg[thisctrl].value: dlg[ctrlname+aft].isVisible=True
            else: dlg[ctrlname+aft].isVisible=False


        # Validation applicable to wings/struts/turbines only
        if pnlid['aftid']=='create_strut'+aft or \
           pnlid['aftid']=='create_turbine'+aft or \
           pnlid['aftid']=='create_wing'+aft:

            # Enforce the nickname a valid variable name
            if re.findall(r'^([A-Za-z][A-Za-z_0-9]*|)$', dlg['nickname'+aft].value): # Accept blank, or, someting that starts with a letter and can then contain letters, numbers, or _
                dlg['nickname'+aft].isValueError = False
                if invalid.get('nickname',0): invalid.pop('nickname') # no longer invalid
                if dlg.get('save'+aft,0):
                    dlg['save'+aft].isEnabled=True
                    if dlg.get('save_button_state'+aft,1): # Default is to save
                        dlg['save'+aft].value=True # restore users chosen state
            else:
                valid=-99 # prevent OK
                dlg['nickname'+aft].isValueError = True 
                if dlg.get('save'+aft,0):
                    dlg['save'+aft].isEnabled=False
                    dlg['save'+aft].value=False # un check it


            if pnlid['aftid']=='create_strut'+aft or \
               pnlid['aftid']=='create_wing'+aft:
                # Auto-select the tail point if they just selected the nose
                if caller=='changed':
                    if thisctrl == 'nose'+aft:
                        if dlg['nose'+aft].selectionCount and not dlg['tail'+aft].selectionCount:
                            dlg['nose'+aft].hasFocus=False
                            dlg['nose'+aft].isEnabled=False
                            dlg['tail'+aft].hasFocus=True
                            dlg['tail'+aft].isEnabled=True


                # Auto-select the join point if they just selected the tail (after seletcing the nose)
                if caller=='changed' and thisctrl == 'tail'+aft and dlg['nose'+aft].selectionCount and dlg['tail'+aft].selectionCount and dlg.get('join'+aft,0) and not dlg['join'+aft].selectionCount:
                    dlg['tail'+aft].hasFocus=False
                    dlg['tail'+aft].isEnabled=False
                    dlg['join'+aft].hasFocus=True
                    dlg['join'+aft].isEnabled=True


            # Fill out their presets if they just chose one
            if thisctrl=='preset'+aft:
                preset=cmdh['preset'+aft]['choices'][dlg['preset'+aft].selectedItem.index] # 'Hydrofoil surf board' , etc
                
                # Need to load their settings into the preset dict here...

                if cmdh['preset'+aft]['values'].get(preset,0):                              # One of ours - not "Your foil: theirs"
                    p=cmdh['preset'+aft]['values'][preset]  # We use the name of the value as the key
                            
                    for v in p: # go through every setting in the preset
                        if not cmdh.get(v,0):
                            continue
                        # Fix the units my presets are in, into the units fusion uses
                        unitid=''
                        if cmdh[v].get('unit',0):
                            unitid=cmdh[v]['unit']       # m or C etc
                        setting=p[v]
                        if units.get(unitid,0):
                            if units[unitid].get('scale',0):
                                setting=setting*units[unitid]['scale']
                            elif units[unitid].get('offset',0):
                                setting=setting+units[unitid]['offset']

                        try:
                            if cmdh[v]['type']=='RadioButtonGroupCommandInput' or cmdh[v]['type']=='DropDownCommandInput': # button / Dropdown
                                if cmdh[v]['type']=='DropDownCommandInput' and dlg[v].selectedItem is None:
                                    dlg[v].listItems.add(" ",True)  # Need to first create the selected object befre we can select a different one
                                dlg[v].selectedItem.index
                                if dlg[v].selectedItem.index >= 0:
                                    dlg[v].listItems[ dlg[v].selectedItem.index ].isSelected=False # Un select previous
                                dlg[v].listItems[setting].isSelected=True # Select preset
                            else:
                                dlg[v].value=setting # set it
                        except:
                            pass    # debugging


               
            if pnlid['aftid']=='create_strut'+aft or \
               pnlid['aftid']=='create_wing'+aft:
                # Compute their chord
                if dlg['nose'+aft].selectionCount and dlg['tail'+aft].selectionCount:
                    dist=dlg['nose'+aft].selection(0).entity.geometry.distanceTo(dlg['tail'+aft].selection(0).entity.geometry) # OK
                    dlg['chord_info'+aft].text=adsk.core.Application.get().activeProduct.unitsManager.formatInternalValue(dist)
                    if invalid.get('chord',0): invalid.pop('chord') # no longer invalid
                    valid=valid+1 # 1 so far


            # Medium
            water=False
            if dlg['medium'+aft].selectedItem.index >= 0: # is -1 if not set
                valid=valid+1 # 2 so far
                if invalid.get('medium',0): invalid.pop('medium') # no longer invalid
                medium=cmdh['medium'+aft]['choices'][dlg['medium'+aft].selectedItem.index] # 'Air', 'Fresh Water', 'Sea Water', 'Any Water', 'Other'
                if medium[-5:] == 'Water': # All 3 that end with "Water"
                    dlg['altitude_group'+aft].isVisible=False # No altitude for water
                    valid=valid+1 # 3 so far (water has no altitude)
                    water=True
                else:
                    dlg['altitude_group'+aft].isVisible=True
                if medium == 'Other':           # Enable the extra stuff they need to tell us
                    valid=valid-3               # 0 now - need to supply density and viscosity
                    dlg['density'+aft].isEnabled=True
                    dlg['density'+aft].isVisible=True
                    dlg['dynamic_viscosity'+aft].isEnabled=True
                    dlg['dynamic_viscosity'+aft].isVisible=True
                    dlg['kinematic_viscosity'+aft].isEnabled=True
                    dlg['kinematic_viscosity'+aft].isVisible=True
                else:                           # Disable what we don't need
                    dlg['density'+aft].isEnabled=False
                    dlg['density'+aft].isVisible=False
                    dlg['dynamic_viscosity'+aft].isEnabled=False
                    dlg['dynamic_viscosity'+aft].isVisible=False
                    dlg['kinematic_viscosity'+aft].isEnabled=False
                    dlg['kinematic_viscosity'+aft].isVisible=False


            if thisctrl=='density'+aft:
                if not pnl.get('toldnodenseyet',0):
                    ui.messageBox("Sorry - the non-Air/non-Water feature will be abailable in the next release.  It does not currently have any effect now.")
                    pnl['toldnodenseyet']=True
            # 'density'
            # 'dynamic_viscosity'
            # 'kinematic_viscosity'


            # Compute Ncrit
            ncrit=''
            if dlg['turbulence'+aft] and dlg['turbulence'+aft].selectedItem:    # Flow conditions
                if dlg['finish'+aft] and dlg['finish'+aft].selectedItem:        # Smoothness
                    valid=valid+2 # 5 so far
                    turb=dlg['turbulence'+aft].selectedItem.index # 'Laminar and clean', 'Average', 'Turbulent and dirty'
                    fin=dlg['finish'+aft].selectedItem.index # 'Very rough', 'Average', 'Clean', 'Very smooth'
                    if turb>=0 and fin>=0:
                        turb=3-turb
                        fin=fin+1
                        # ncrit=3*finish + turb-1 +(turb==3&&finish<4)-(turb==1&&finish>1); 
                        # gives: f1t1=n3 f1t2=n4 f2t1=n5 f1t3=n6 f2t2=n7 f3t1=n8 f2t3=n9 f3t2=n10 f4t1=n11 f3t3=n12 f4t2=n13 f4t3=n14
                        ncrit=3*fin + turb-1 
                        if  turb==3 and fin < 4 :
                            ncrit = ncrit+1
                        if  turb==1 and fin > 1 :
                            ncrit = ncrit-1
                        dlg['N']=ncrit # for insert2dwing to use in a moment
                        ncrit = " N" + str(ncrit)
                        if invalid.get('finish',0): invalid.pop('finish') # no longer invalid
                        if invalid.get('turbulence',0): invalid.pop('turbulence') # no longer invalid

            if pnlid['aftid']=='create_strut'+aft or \
               pnlid['aftid']=='create_wing'+aft:
                # Compute Re
                if dlg['targettemperature'+aft]:
                    valid=valid+1 # 6 so far
                    if dist:
                        if dlg['targetspeed'+aft] and dlg['targetspeed'+aft].value>0:
                            valid=valid+1 # 7 so far
                            if dlg['targetaltitude'+aft]:
                                valid=valid+1 # 8 so far
                                if dlg['medium'+aft].selectedItem.index >= 0: # Water of some kind (is -1 if not set)
                                    medium=cmdh['medium'+aft]['choices'][dlg['medium'+aft].selectedItem.index] # 'Air', 'Fresh Water', 'Sea Water', 'Any Water', 'Other'

                                    chord=dist/100
                                    s=dlg['targetspeed'+aft].value/100
                                    a=dlg['targetaltitude'+aft].value/100
                                    t=dlg['targettemperature'+aft].value -273.15
                                    Re=getRe( medium, chord , s , a , t )
                                    if Re!=dlg.get('re',0): # Only tell them suff when they change stuff
                                        if water:
                                            vlog("Re {:,.0f} results from {:.5g}m chord at {:.5g}m/s speed in {:.5g}C temp {}".format(Re,chord,s,t, medium))
                                        else:
                                            vlog("Re {:,.0f} results from {:.5g}m chord at {:.5g}m/s speed in {:.5g}C temp at {:.5g}m altitude in {}".format(Re,chord,s,t,a, medium))
                                        #eprint("Re {:12,.0f} results from {}m chord at {}m/s speed in {}C temp at {}m altitude".format(Re,chord,s,t,a))
                                    dlg['re_info'+aft].text="{:,.0f}{}".format(Re,ncrit)
                                    dlg['re']=Re        # for insert2dwing to use in a moment
                                    dlg['chord']=chord  # for insert2dwing to use in a moment
                                    if Re>0:
                                        valid=valid+1 # 7 so far
                                        if invalid.get('re',0): invalid.pop('re') # no longer invalid
                                    #adsk.core.Application.get().activeProduct.unitsManager.formatInternalValue(dist)

                                    #eprint("Target Re=" + str(getRe( 'AIR', dist/100, dlg['targetspeed'+aft].value/100 , dlg['targetaltitude'+aft].value/100 , dlg['targettemperature'+aft].value-273.15  )))

                                    # Fill in the hidden "hard stuff" every time they change the preset (unless they are about to enter the hard stuff themsevles)
                                    if thisctrl=='preset'+aft and medium != 'Other': 
                                        if water: 
                                            d=Water_Density(medium,t)
                                            dlg['density'+aft].value='{}'.format(d)
                                            v=Water_Viscosity(t)
                                            dlg['dynamic_viscosity'+aft].value='{}'.format(v)
                                        else:
                                            d=Altitude_to_Density(a)
                                            dlg['density'+aft].value='{}'.format(d)
                                            v=Gas_Viscosity(medium,t)
                                            dlg['dynamic_viscosity'+aft].value='{}'.format(v)
                                        if d:
                                            dlg['kinematic_viscosity'+aft].value='{}'.format(v/d)


            if pnlid['aftid']=='create_turbine'+aft:
                if dlg['targetspeed'+aft] and dlg['targetspeed'+aft].value>0:
                    if invalid.get('targetspeed',0): invalid.pop('targetspeed') # no longer invalid
                if dlg['targettemperature'+aft]:
                    if invalid.get('targettemperature',0): invalid.pop('targettemperature') # no longer invalid
                if dlg['targetaltitude'+aft]:
                    if invalid.get('targetaltitude',0): invalid.pop('targetaltitude') # no longer invalid
                # Auto-select the hub_nose if they just selected the center_line
                if caller=='changed':
                    if thisctrl == 'centerline'+aft:
                        if dlg['centerline'+aft].selectionCount:                # They've picked a lone
                            if dlg['hub_nose'+aft].selectionCount:              # They already picked a hub nose
                                if not dlg['hub_edge'+aft].selectionCount:           # They already picked a hub nose
                                    dlg['centerline'+aft].hasFocus=False        # Auto-select the hub edge
                                    dlg['centerline'+aft].isEnabled=False
                                    dlg['hub_edge'+aft].hasFocus=True
                                    dlg['hub_edge'+aft].isEnabled=True
                            else:                                               # No hub_nose selected yet
                                dlg['centerline'+aft].hasFocus=False
                                dlg['centerline'+aft].isEnabled=False
                                dlg['hub_nose'+aft].hasFocus=True               # Auto-select the hub nose
                                dlg['hub_nose'+aft].isEnabled=True

                # Auto-select the hub edge point if they just selected the hub_nose (after seletcing the centerline)
                if caller=='changed' and thisctrl == 'hub_nose'+aft and dlg['centerline'+aft].selectionCount and dlg['hub_nose'+aft].selectionCount and dlg.get('hub_edge'+aft,0) and not dlg['hub_edge'+aft].selectionCount:
                    dlg['hub_nose'+aft].hasFocus=False
                    dlg['hub_nose'+aft].isEnabled=False
                    dlg['hub_edge'+aft].hasFocus=True
                    dlg['hub_edge'+aft].isEnabled=True

                if dlg['centerline'+aft].selectionCount:
                    dist=dlg['centerline'+aft].selection(0).entity.length # dlg['nose'+aft].selection(0).entity.geometry.distanceTo(dlg['tail'+aft].selection(0).entity.geometry) # OK
                    dlg['root_chord_info'+aft].text=adsk.core.Application.get().activeProduct.unitsManager.formatInternalValue(dist)
                    if invalid.get('root_chord_info',0): invalid.pop('root_chord_info') # no longer invalid
                    valid=valid+1

                if dlg['hub_nose'+aft].selectionCount:
                    if invalid.get('hub_nose',0): invalid.pop('hub_nose') # no longer invalid
                    valid=valid+1

                if dlg['hub_edge'+aft].selectionCount:
                    if invalid.get('hub_edge',0): invalid.pop('hub_edge') # no longer invalid
                    valid=valid+1

                if dlg['centerline'+aft].selectionCount \
                   and dlg['hub_nose'+aft].selectionCount \
                   and dlg['hub_edge'+aft].selectionCount:
                    center_line=dlg['centerline'+aft].selection(0).entity
                    root_chord=dlg['centerline'+aft].selection(0).entity.length / 100       # in meters
                    hub_nose=dlg['hub_nose'+aft].selection(0).entity
                    hub_edge=dlg['hub_edge'+aft].selection(0).entity
                    center_point=center_line.endSketchPoint
                    if not hub_nose.geometry.distanceTo(center_point.geometry) > 0:
                        center_point=center_line.startSketchPoint
                    hub_radius=hub_edge.geometry.distanceTo(center_point.geometry) / 100    # in meters
                    if root_chord>0 and hub_radius>0:
                        if invalid.get('hub_radius',0): invalid.pop('hub_radius') # no longer invalid


        else: # Not a foil (no nickname)        
            valid=-99

        #if(valid>=6):   # We need all 5 things (nose, tail, finish, medium, flow, velocity, altitude (if not water) & temp ... before we can do the foil)
        if not len(invalid):                                                    # If everything needed has been removed from the invalid dict:
            args.areInputsValid = True
            return True
        else:                                                                   # Something still invalid exists
            args.areInputsValid = False
            eprint(invalid)
            return False

    except:
        eprint(caller + ' event failed: {}'.format(traceback.format_exc()))
        if ui:
            ui.messageBox(program_name+' event failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))



foilinfo=[ # Supporting info for data that might get insewrted into their user parameters
            {'alpha':'Ideal angle of attack (AoA) for foil: '}, # '13.9', + Foil_fn
            {'Cm':'Pitching-moment coefficient relative to quarter chord (center of pressure at design AoA)'}, # '0.9837',
            #{'Foil_fn':''}, # cannot have text parameters: 'Original filename of the input airfoil'}, # 'spline_foil_v13006.dat-s17_n17s0.dat',
            #'cmt' => 'NEWv1.20200425 s(0) foildb2020/e377m.dat (sim 0.000193213738 ) l3 Foil spline 17pts', # foil comments
            {'Re':'Closest test Reynolds number found corresponding to your input criteria - see user_Re'},    # 100000000, # real Re
            {'n':'Closest test log(critical angle) - transition criterion determined from your flow and finish input'}, # 11,
            #{'chord':[ 'cm', 'straight distance from nose to tail' ]}, # 123
            {'r':'criteria used to determine "ideal" (6=bell-curve weighted overall best using +/- 3 significant degrees AoA from ideal)'}, # 1,
            {'CL':'Coefficient of lift at design AoA'}, # '1.5369',
            {'CD':'Coefficient of drag at design AoA'}, # '0.00372',
            {'clcd':'CL/CD (foils) or 1/CD (symmetric) - bigger is always better'}, # '0.00372',
            {'CDf':'friction-drag component contributing to CD'}, # '0.0016',
            {'CDpres':'pressure-drag component contributing to CD'}, # '0.0016',
            {'good':'foil selection criteria: max weighted (see "r") average "clcd"'}, # '0.00372',
            {'CDp':'dynamic pressure max'}, # '0.0016',
            {'Cpmin':'Minimum pressure extent (cavitation indicator) at design AoA'}, # '-21.4023',
            {'sym':'Degree of foil symmetry. 0=exactly symmetric, >0.00125 non-symmetric'}, # '0.097049938590344',
            {'cmt':''}, # 'Spline conversion data (sim = similarity-match with original foil data)'}, # 'NEWv1.20200425 s(0) foildb2020/v13006.dat (sim 0.000016577733 ) l3 Foil spline 17pts',
            {'Top_Xtr':'Top position of forced transition from laminar to turbulent at design AoA'}, # '0.00146'
            {'Bot_Xtr':'Bottom position of forced transition from laminar to turbulent at design AoA'}, # '0.0014',
            # {'Top_Itr':'.'}, # '0.9837',
            # {'Bot_Itr':'.'}, # '78.0185',
            {'xver':'solver version number'}, # '6.99',
            {'diter':'solution iteration count'}, # '6.99',
            # {'src':'solver machine ID'}, # '6.99',
            # {'ok':''}, # 1,
            # {'s':''}, # 0,
            #{'ver':'insertion processor version number'}, # 'v.1.20200504',
            {'iver':'solver manager version number'}, # '1.20200505',
            {'id':''}, # 1,
            # {'xy':''} # [ 1}, 0, '0.855242605109347', '0.0117125705324037', '0.602519634254835', '0.0275105856224779', '0.37458813296931', '0.0368627176605416', '0.190731108083199', '0.0377396028682893',
            ]



# Get the current sketch, or if not in a sketch, create a suitable new sketch and project anything needed into it
def MySketch(*proj):
    app = adsk.core.Application.get()

    sketch = app.activeEditObject                                           # Get the current sketch?
    # Get current sketch, or, prepare to create new one if they're not in one right now (note: creating a new sketch breaks the UI input - erases their selection points)
    if not sketch or sketch.objectType != 'adsk::fusion::Sketch':
        rootComp = None
        try:
            for bestComp in proj:
                rootComp=bestComp.parentSketch.parentComponent             # Try to create new sketches in the correct component (whichever works first)
                if rootComp: 
                    break
            if not rootComp: rootComp = design.rootComponent                # Default to the root component of the active design.
            sketches = rootComp.sketches                                    # Create a new sketch on the same plane as what the user selected the nose in
        except:
            rootComp = design.rootComponent                                 # Default to the root component of the active design.
            sketches = rootComp.sketches                                    # Create a new sketch on the same plane as what the user selected the nose in
        # CAUTION - next line breaks the users input
        sketch = sketches.add( proj[-1].parentSketch.referencePlane )       # Use same plane as whatever their chosen nose was (XY, XZ, or YZ)

    # project any foreign points into our current sketch (needed so the X,Y makes sense later)
    for bestComp in proj:
        if bestComp.parentSketch.name != sketch.name:                       # project any foreign things (chord lines, points) into here
            proj=sketch.project(bestComp)
            proj.isConstruction=True

    return sketch



#################################################################################
####                                                                          ###
##                              Do the Work at last!!                          ##
####                                                                          ###
#################################################################################
def insertTurbineUI(pnlid,args,inputs):
    global VERSION, pnl, userdata, settings_file, foilinfo
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        sharejson={}

        panel=pnlid['mywhere'] + '_' + pnlid['aftid'] # 'sketch_airfoil_command_aft' + '_' + 'menuid':'create_cowling_aft'
        dlg=pnl[panel]

        pnl['calcstart']=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())

        # Set up some constants...
        nickname=dlg['nickname'+aft].value                                      # Triggers inserting user parms if named
        center_line=dlg['centerline'+aft].selection(0).entity
        root_chord=dlg['centerline'+aft].selection(0).entity.length / 100       # in meters
        hub_nose=dlg['hub_nose'+aft].selection(0).entity
        hub_edge=dlg['hub_edge'+aft].selection(0).entity
        center_point=center_line.endSketchPoint
        if not hub_nose.geometry.distanceTo(center_point.geometry) > 0:
            center_point=center_line.startSketchPoint
        hub_radius=hub_edge.geometry.distanceTo(center_point.geometry) / 100    # in meters
        in_speed=dlg['targetspeed'+aft].value / 100                             # in meters / sec

        # CAUTION - next line loses the users selection inputs above
        sketch = MySketch(center_line,hub_nose,hub_edge)                         # Get the current sketch (creates new if we're not in one; last element provides the plane, first element provides the component)
        sketchPoints = sketch.sketchPoints

        # Name the sketch for them:
        if nickname and sketch.name[:6]=='Sketch':
            sketch.name=nickname+'_turbine'                                     # Name their sketch for them, if they've not already done that themselves

        #hub_Re=dlg['re']        # Inserted by the validate code - not relevant - speed is incoming airflow, not profile speed
        N=dlg['N']              # Inserted by the validate code

        # Test setup
        rpm=1400
        rps=rpm/60
        num_profiles=10             # Testing - let us do 10 (that's 9 segments) - future: only do new ones when we have new foil shapes at new Re's we support
        prop_radius=root_chord*9     # len goes from center to tip: diameter will be 10x chord - note that the actual "blade length" is less by the hub radius
        blade_len=prop_radius-hub_radius 
        energy=16/27                # Placeholder: best possible - betz limit - how much power we plan to extract from the flow
        le_points = adsk.core.ObjectCollection.create() # Leading-edge spline
        te_points = adsk.core.ObjectCollection.create() # Trailling edge line

        # Do all sections
        chord_speed=[]                                                          # store station results so later ones can refer back to earlier ones
        for station in range(0,num_profiles):                                   # 0 to 9 - for all 10 foils that comprise our 9 segments
            section_radius=hub_radius+station*(blade_len/num_profiles)
            section_speed=rps * math.pi * 2 * (section_radius)                  # profile speed in M/S
            section_chord=(num_profiles-station)*root_chord/num_profiles        # 10 down to 1 - initially vary the chord in % 
            if station>4: # 5+
                section_chord=chord_speed[station-1]/ section_speed             # This forces the outer half of the blade to have the same Re to the tip
            chord_speed.append( section_chord * section_speed )                 # so we can keep Re constant if we want

            zero_aoa=math.atan((energy * in_speed) / section_speed ) / math.pi * 180 # Work out the needed pitch at this section for the RPM and speed

            # Compute Re
            medium=cmdh['medium'+aft]['choices'][dlg['medium'+aft].selectedItem.index] # 'Air', 'Fresh Water', 'Sea Water', 'Any Water', 'Other'
            a=dlg['targetaltitude'+aft].value/100
            t=dlg['targettemperature'+aft].value -273.15
            Re=getRe( medium, section_chord , section_speed , a , t )
            if 1:
                if medium[-5:] == 'Water': # All 3 that end with "Water"
                    vlog("Section {}. Re {:,.0f} results from {:.5g}m chord at {:.5g}m/s speed in {:.5g}C temp {}".format(station, Re, section_chord, section_speed, t, medium))
                else:
                    vlog("Section {}. Re {:,.0f} results from {:.5g}m chord at {:.5g}m/s speed in {:.5g}C temp at {:.5g}m altitude in {}".format(station, Re, section_chord, section_speed, t, a, medium))

            section_foil=bestFoil( Re=Re, N=N, strut=False, TextInfo=True) # Find hub foil that is the closest Re match to the one we want

            tail=sketchPoints.add( adsk.core.Point3D.create( hub_edge.geometry.x, 0.0, -section_radius*100) ) # Insert a point to indicate the tail, and where the rotation-join will be (not using hub_edge since it might be from wrong sketch)
            nose=sketchPoints.add( adsk.core.Point3D.create( hub_edge.geometry.x-section_chord*100, 0.0, -section_radius*100) ) # And the nose, to its left


            insertFoil( sketch=sketch, 
                        nose=nose,           # dlg['nose'+aft].selection(0).entity
                        tail=tail,           # dlg['tail'+aft].selection(0).entity
                        join=tail,           # Always rotatae about the tail, so the trailling edge is a straight line
                        usefoil=section_foil,
                        rotate=-1, # callee uses -section_foil['alpha'],
                        flip=-1,              # anti-clockwise?
                        extrarotate=-zero_aoa, # Additional (on top of AoA, if any) rotation to apply (typically used for propeller pitch based on RPM, speed, and inflow)
                        wrapline=center_line,  # Center of a cylinder that the foil will be bent around
                        wrapstart=hub_edge, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not have to be part of the foil - only the X and distance-from-line is used.)
                        endscale=0,
                        textInfo=True,      # Tell the user what we did in the text info area (and, for errors, with UI popups)
                        constrain=False,
                        sharejson=sharejson) # sharejson is output

            te_points.add(sharejson['points'].item(0)) # Trailling edge point
            midpt=int((sharejson['points'].count-1)/2)
            le_points.add(sharejson['points'].item(midpt)) # Leading edge point

        le_line=sketch.sketchCurves.sketchFittedSplines.add(le_points) 
        te_line=sketch.sketchCurves.sketchFittedSplines.add(te_points) # Normally a straight line at present

    # Error handling
    except:
        if ui:
            ui.messageBox(program_name+' insertTurbineUI failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))





#################################################################################
####                                                                          ###
##                              Do the Work at last!!                          ##
####                                                                          ###
#################################################################################
def insert2DWing(pnlid,args,inputs):
    global VERSION, pnl, userdata, settings_file, foilinfo
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        panel=pnlid['mywhere'] + '_' + pnlid['aftid'] # 'sketch_airfoil_command_aft' + '_' + 'menuid':'create_cowling_aft'
        dlg=pnl[panel]

        if dlg.get('votebox'+aft,0) and dlg['votebox'+aft].value:               # Not a command
            return True
        if dlg.get('nickname'+aft,None) is None:                                # Not a command
            return True


        pnl['calcstart']=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())


        # Set up some constants...
        cache={} # sketches.add() breaks user selections input, so cache selections now
        nickname=dlg['nickname'+aft].value                                      # Triggers inserting user parms if named
        nose=dlg['nose'+aft].selection(0).entity
        tail=dlg['tail'+aft].selection(0).entity
        join=None
        if dlg.get('join'+aft,0) and dlg['join'+aft].selectionCount:
            join=dlg['join'+aft].selection(0).entity
        else:
            eprint("No join chosen") # sometimes misses this?

        if dlg.get('up'+aft,0) and dlg['up'+aft].selectedItem.index:            # Up is item 0, so, item 1 (true) is inverted
            (flip,dflip)=(-1,-1)                                                # dflip for user parms, flip for us (might be reversed if we rotated >90 degrees...)
        else:
            (flip,dflip)=(1,1) 

        sketch = app.activeEditObject                                           # Get the current sketch?
        # Get current sketch, or, prepare to create new one if they're not in one right now (note: creating a new sketch breaks the UI input - erases their selection points)
        if not sketch or sketch.objectType != 'adsk::fusion::Sketch':
            rootComp = None
            try:
                if join: rootComp=join.parentSketch.parentComponent             # Try to create new sketches in the correct component
                if not rootComp: rootComp=nose.parentSketch.parentComponent
                if not rootComp: rootComp = design.rootComponent                # Default to the root component of the active design.
                sketches = rootComp.sketches                                    # Create a new sketch on the same plane as what the user selected the nose in
            except:
                rootComp = design.rootComponent                                 # Default to the root component of the active design.
                sketches = rootComp.sketches                                    # Create a new sketch on the same plane as what the user selected the nose in
            # CAUTION - next line breaks the users input
            sketch = sketches.add( nose.parentSketch.referencePlane )           # Use same plane as whatever their chosen nose was (XY, XZ, or YZ)

        # project any foreign points into our current sketch (needed so the X,Y makes sense later)
        if nose.parentSketch.name != sketch.name:                               # project any foreign point into here
            proj=sketch.project(nose)
            if proj.count: nose=proj.item(0)
        if tail.parentSketch.name != sketch.name:
            proj=sketch.project(tail)
            if proj.count: tail=proj.item(0)

        rotate=360                                                              # Flag so we know whether or not to rotate later (<360 means yes)
        if join:                                                                # Only rotate if they selected a join point
            rotate=0
            if join.parentSketch.name != sketch.name:
                proj=sketch.project(join)
                if proj.count:
                    join=proj.item(0)
                    join.isConstruction=True
        else:
            join=nose                                                           # Default to join to nose-point dlg['nose'+aft].selection(0).entity
            eprint("Not auto-rotating") # sometimes misses this?

        cache['nose'+aft]=nose
        cache['tail'+aft]=tail
        cache['join'+aft]=join

        constrain=dlg.get('constrain'+aft,0) and dlg['constrain'+aft].value     # Make this optional, since it is so slow.
        strut=panel.find('strut') >= 0                                          # struts have the word "strut" in the panel name
        doendcap=dlg.get('endcap'+aft,0) and dlg['endcap'+aft].value            # Do they want rounded ends
        if doendcap and dlg.get('enddist'+aft,0): endscale=dlg['enddist'+aft].value/200      # How pointy to make the endcaps
        else: endscale=0

        Re=dlg['re']        # Inserted by the validate code
        N=dlg['N']          # Inserted by the validate code
        chord=dlg['chord']  # Inserted by the validate code

        # Find foil that is the closest Re match to the one we want
        usefoil=bestFoil( Re=Re, N=N, strut=strut, TextInfo=True)

        # Insert computed and foil data into user parameters (before they get lost when we create a new sketch...)
        sharejson={}
        # Insert computed
        for parms in foilinfo:
            for pkey in parms:
                desc=parms[pkey]
                if desc: # blank means skip
                    pname=nickname + aft + '_' + pkey
                    #val = adsk.core.ValueInput.:createByString("5 mm");
                    valr = usefoil.get(pkey,0)
                    if isinstance(valr, str): valr=float(valr)
                    val = adsk.core.ValueInput.createByReal(valr)
                    unit=''
                    if pkey=='alpha':   # add text data into the comments
                        desc=desc + usefoil.get('Foil_fn','')
                        unit='deg'
                        val = adsk.core.ValueInput.createByString('{} deg'.format(valr))
                    if pkey=='xver':   # add text data into the comments
                        desc=desc + ', {} version:{:1.8f} db:{:1.8f}'.format(program_name,VERSION,float(foildb2020.VERSION(0)))
                    sharejson[pkey]=valr
                    if nickname:
                        if design.userParameters.itemByName(pname):
                            vlog("Not adding user parameter {} because it already exists in the parameters".format(pname))
                        else:
                            design.userParameters.add(pname, val, unit, desc)
        if nickname:
            pname=nickname +aft+ '_chord' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByString('{} m'.format(chord)), 'm', 'straight distance from nose to tail')
            pname=nickname +aft+ '_user_Re' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal(Re), '', 'Your computed Reynolds Number')
            pname=nickname +aft+ '_user_ncrit' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal(N), '', 'Your computed log(critical angle)')
            pname=nickname +aft+ '_user_flip' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal(dflip), '', 'Lift(1) or Downforce(-1)')
            pname=nickname +aft+ '_user_ver' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal(VERSION), '', program_name+' version number')
            pname=nickname +aft+ '_user_dbver' # Add this computed value separately
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal(foildb2020.VERSION(0)), '', program_name+' foil database version number')

        # Insert user entered
        for userinfo in cmdl:
            if userinfo.get('id',0) and dlg.get(userinfo['id'],0) and userinfo.get('type','') and userinfo.get('name','') and dlg[userinfo['id']].isVisible:
                pname=nickname + aft+'_user_' + userinfo['id']
                if userinfo['type']=='ValueInput':
                    valr = dlg[userinfo['id']].value
                    if isinstance(valr, str): valr=float(valr)
                    val = adsk.core.ValueInput.createByReal(valr)
                    sharejson[ userinfo['id'] ]=valr
                    if nickname:
                        if design.userParameters.itemByName(pname):
                            vlog("Not adding user parameter {} because it already exists in the parameters".format(pname))
                        else:
                            design.userParameters.add(pname, val, userinfo.get('unit',''), userinfo.get('tip',''))
                elif userinfo['type']=='StringValueInput' or userinfo['type']=='BoolValueInput':
                    if dlg[userinfo['id']].value != '': sharejson[ userinfo['id'] ]=dlg[userinfo['id']].value
                elif userinfo['type']=='SelectionInput':
                    ent=cache[userinfo['id']]
                    if ent.objectType == 'adsk::fusion::SketchPoint':
                        sharejson[ userinfo['id'] ]='({},{},{})'.format( ent.geometry.x, ent.geometry.y, ent.geometry.z) 
                    elif ent.objectType == 'adsk::fusion::SketchLine':
                        sharejson[ userinfo['id'] ]='({},{},{})-({},{},{})'.format( ent.startSketchPoint.geometry.x, 
                                                                                    ent.startSketchPoint.geometry.y,
                                                                                    ent.startSketchPoint.geometry.z,
                                                                                    ent.endSketchPoint.geometry.x,
                                                                                    ent.endSketchPoint.geometry.y,
                                                                                    ent.endSketchPoint.geometry.z)
                elif userinfo['type']== 'StringValueInput' or userinfo['type']== 'BoolValueInput': 
                    sharejson[ userinfo['id'] ]=dlg[userinfo['id']].value
                elif userinfo['type']== 'ButtonRowCommandInput' or userinfo['type']== 'RadioButtonGroupCommandInput' or userinfo['type']== 'DropDownCommandInput':
                    sharejson[ userinfo['id'] ]=dlg[userinfo['id']].selectedItem.index
                #else:
                #    eprint("cant save non-value parm {} {}".format(userinfo['id'],userinfo.get('type','')))


        # Name the sketch for them:
        if nickname and sketch.name[:6]=='Sketch':
            sketch.name=nickname+'_foil'                                        # Name their sketch for them, if they've not already done that themselves


        # Perform the insert
        insertFoil( sketch=sketch, 
                    nose=nose,           # dlg['nose'+aft].selection(0).entity
                    tail=tail,           # dlg['tail'+aft].selection(0).entity
                    join=join,
                    usefoil=usefoil,
                    rotate=rotate,    
                    flip=flip,    
#                    extrarotate=0, # Additional (on top of AoA, if any) rotation to apply (typically used for propeller pitch based on RPM, speed, and inflow)
#                    wrapline=None,  # Center of a cylinder that the foil will be bent around
#                    wrapstart=None, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not have to be part of the foil - only the X and distance-from-line is used.)
                    endscale=endscale,
                    textInfo=True,      # Tell the user what we did in the text info area (and, for errors, with UI popups)
                    constrain=constrain,
                    sharejson=sharejson) 

        if sharejson.get('points',0):  # Not serializable
            del sharejson['points']

        # Return everything about this foil to the caller
        sharejson['chord']=chord
        sharejson['user_Re']=Re
        sharejson['user_ncrit']=N
        sharejson['user_flip']=dflip
        sharejson['nickname']=nickname
        sharejson['ver']=VERSION
        sharejson['dbver']=foildb2020.VERSION(0)
        sharejson['count']=1+ userdata.get('count',0)
        userdata['count']=sharejson['count']
        sharejson['now']=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
        sharejson['panel']=panel
        for i in ('calcstart', 'opened', 'loaded', 'openc'):
            sharejson[i]=pnl[i]


        # Let us know what they did if they checked the box to allow it
        if dlg.get('share'+aft,0) and dlg['share'+aft].value:
            #crashes - _thread.start_new_thread(web_req, ('u=u1.20200506&v=1.20200503&a=_aft&p=Airfoil_Tools',))
            web_nbreq('s='+urllib.parse.quote(json.dumps(sharejson), safe='')) #non-blocking socket. might need to do this first, so we get a chance to poll it?  or hook CommandHandler?
        userdata['count']=sharejson['count']

        # Insert metadata that our re-computer might need into user parms
        if nickname:
            pname=nickname + aft + '_json'
            if not design.userParameters.itemByName(pname): design.userParameters.add(pname, adsk.core.ValueInput.createByReal( sharejson['count'] ), '', json.dumps(sharejson) )

        userdata['last']=json.dumps(sharejson) # remember their most recent settings, so we can offer then again in future
        save_user_settings(ui,settings_file) 

        # Replace this if we decide in future not to hook all events
        if 0:
            if web_nbreq(None): maxt=2
            else: maxt=0 # proccess any non-blocking operations, wating upto max 2s
            while maxt>0 and web_nbreq(None): # proccess any non-blocking operations
                eprint('waiting {}'.format(maxt))
                time.sleep(0.25)
                maxt=maxt-0.25

    # Error handling
    except:
        if ui:
            ui.messageBox(program_name+' insert2DWing failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))







#################################################################################
####                                                                          ###
##                           The real work gets done here                      ##
####                                                                          ###
#################################################################################
def insertFoil( sketch=None,
                nose=None,           # dlg['nose'+aft].selection(0).entity
                tail=None,           # dlg['tail'+aft].selection(0).entity
                join=None,
                usefoil=None,        # from bestFoil()
                rotate=None,    # <360 means they want best cl/cd auto-rotate applied
                flip=None,      # Lift or downforce?
                extrarotate=0, # Additional (on top of AoA, if any) rotation to apply (typically used for propeller pitch based on RPM, speed, and inflow)
                wrapline=None,  # Center of a cylinder that the foil will be bent around
                wrapstart=None, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not have to be part of the foil - only the X and distance-from-line is used.)
                endscale=None,
                textInfo=None,
                constrain=None,
                sharejson=None):     # Return info
    global VERSION,foilinfo

    try:

        (nosex,nosey,nosez)=(nose.geometry.x, nose.geometry.y, nose.geometry.z)
        (tailx,taily,tailz)=(tail.geometry.x, tail.geometry.y, tail.geometry.z)
        scale=nose.geometry.distanceTo(tail.geometry) # OK

        # Create an object collection for the points.
        points = adsk.core.ObjectCollection.create() 
        sketchPoints = sketch.sketchPoints
        dim = sketch.sketchDimensions

        joindx=0    # So we can constrain the CM to the nose later
        joindy=0
        CM = usefoil.get('Cm',0)
        if isinstance(CM, str): CM=float(CM)
        CM=0.25-CM # CM is relative to quarter chord

        # Decide where to join and if to rotate by AoA or not (based on users join point selection)
        if rotate<360: # rotate=0 Indicates they selected a join point or line
            if rotate<0:
                rotate = -usefoil.get('alpha',0) # if caller was negative, it means they want a rotate the other way
            else:
                rotate = usefoil.get('alpha',0)
            if isinstance(rotate, str): rotate=float(rotate)
            if join.objectType=='adsk::fusion::SketchLine':
                (joinstart, joinend) = (join.startSketchPoint, join.endSketchPoint)
                if joinstart.geometry.distanceTo(nose.geometry) > joinend.geometry.distanceTo(nose.geometry): # use their nose selection as the correct orientation to the real front, regardless of what the "start" of the input line might be
                    (joinstart, joinend) = (joinend, joinstart)
                if abs(joinstart.geometry.x-nosex) > 0.000001 or abs(joinstart.geometry.y-nosey) > 0.000001 or abs(joinend.geometry.x-tailx) > 0.000001 or abs(joinend.geometry.y-taily) > 0.000001:
                    if textInfo:
                        vlog('** CAUTION: Your join line is in a different location to your chord line - insertion point may be unreliable **')
                joindx=CM*(joinend.geometry.x - joinstart.geometry.x ) 
                joindy=CM*(joinend.geometry.y - joinstart.geometry.y ) 
                join=sketchPoints.add( adsk.core.Point3D.create( joinstart.geometry.x + joindx, joinstart.geometry.y + joindy, 0) ) # Insert a point to indicate where the rotation-join is, being the CM...

        (joinx,joiny,joinz)=(join.geometry.x, join.geometry.y, join.geometry.z)     # will be nose unless otherwise specified
        nose_tail_angle=math.atan2(taily - nosey, tailx - nosex) * 180 / math.pi    # if it's not horizontal or is "right to left", we need to adjust how we output this (0=nose on left, 180=right, -90=nose-up, -45=nose-up-and-left, -135=nose-up-and-right, 135=nose-down-and-right, 90=nose-down)

        if nose_tail_angle > 90 or nose_tail_angle < -90:
            flip=flip*-1 # we rotate to orient it the way they want, which means we need to flip if we go past vertical (while still respecting their origianl flip request)

        xy=usefoil['xy'] # get the points

        # simple clamp
        (splinex,spliney)=jspline(2,0,0,1,points_to_xy(xy)) # expand them not too much (first 2 is how much)
        splinex.pop()
        spliney.pop()
        splinex[-1]=splinex[0] # Always is anyway, but let us be certain
        spliney[-1]=spliney[0] # Always is anyway, but let us be certain
        splinez = [0.0] * len(splinex) # Might get used if wrapping around a cyl

        # join (kinda more rounded, but skips a few points at the tail)
        # (splinex,spliney)=jspline(2,0,0,0,points_to_xy(xy)) # expand them not too much (first 2 is how much)

        #eprint("pline 1 l={}".format(len(splinex)))

        if constrain:
            shifto=1/8+1/16+1/32+1/64 # hopefully a distance that is extrmeely unlikely to exactly co-incide with any existing geometry in the users sketch (to prevent auto-constraints appearing)
            shifto=0 # Disable this now
        else:
            shifto=0

        middle=int((len(splinex)-1)/2)

        # Find approximate camber Y point to drop the CM onto
        cmx=CM
        cmy=0
        for i in range(middle,len(splinex)): # find closest bottom point
            if splinex[i]>cmx:
                cmy=spliney[i-1]
                break
        for i in range(0,middle): # find top
            if splinex[i]<cmx:
                cmy=flip * (cmy + 0.5*abs(cmy-spliney[i-1]))
                break
        # move the CM to match the foil
        if nose_tail_angle: # put it the way they asked for next
            (x,y)=(cmx,cmy)
            cmx= x * math.cos(-nose_tail_angle*math.pi/180) + y*math.sin(-nose_tail_angle*math.pi/180) 
            cmy= -x * math.sin(-nose_tail_angle*math.pi/180) + y*math.cos(-nose_tail_angle*math.pi/180)
        if ( rotate>0 and rotate<360 ) or extrarotate:  # tilt to to the optimal AoA first
            (x,y)=(cmx+(nosex-joinx)/scale,cmy+(nosey-joiny)/scale) # test rotate - negative is anticlockwise.
            cmx=  x * math.cos(flip*(rotate+extrarotate)*math.pi/180) + y * math.sin(flip*(rotate+extrarotate)*math.pi/180) -(nosex-joinx)/scale
            cmy= -x * math.sin(flip*(rotate+extrarotate)*math.pi/180) + y * math.cos(flip*(rotate+extrarotate)*math.pi/180) -(nosey-joiny)/scale
        if not wrapline:
            cmpt=sketchPoints.add(adsk.core.Point3D.create( cmx*scale+nosex+shifto, cmy*scale+nosey+shifto, 0.0))
        eprint('rotate={} nose_tail_angle={} cmx={} cmy={} extra={} total={}'.format(rotate,nose_tail_angle,cmx,cmy,extrarotate,(rotate+extrarotate)))

        for i in range(0,len(splinex)): # The last one will connect back to the first (it's the same as the first anyhow) - fusion notices this and drops it.
            # maybe we should create them all someplace constrained, then move them?
            spliney[i]=spliney[i]*flip

            if nose_tail_angle: # put it the way they asked for next
                (x,y)=(splinex[i],spliney[i])
                splinex[i]= x * math.cos(-nose_tail_angle*math.pi/180) + y*math.sin(-nose_tail_angle*math.pi/180) 
                spliney[i]= -x * math.sin(-nose_tail_angle*math.pi/180) + y*math.cos(-nose_tail_angle*math.pi/180)

            if ( rotate>0 and rotate<360 ) or extrarotate:  # tilt to to the optimal AoA first
                (x,y)=(splinex[i]+(nosex-joinx)/scale,spliney[i]+(nosey-joiny)/scale) # test rotate - negative is anticlockwise.
                splinex[i]=  x * math.cos(flip*(rotate+extrarotate)*math.pi/180) + y * math.sin(flip*(rotate+extrarotate)*math.pi/180) -(nosex-joinx)/scale
                spliney[i]= -x * math.sin(flip*(rotate+extrarotate)*math.pi/180) + y * math.cos(flip*(rotate+extrarotate)*math.pi/180) -(nosey-joiny)/scale

# Wrap foil around cyl:
# a) translate point to common starting line
# b) rotate by X distance around circumference (new X and Z - Y is untouched)
# wrapline=None,  # Center of a cylinder that the foil will be bent around - this is a tangent to the chord, at some Z distance away
# wrapstart=None, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not 
#                   have to be part of the foil - only the X and distance-from-line is used.)

            # Props/Turbines will rotate about the Y axis in the Z plane

            #wrapstart=tail # testing
            #wrapline=tail # testing
#            wrapline=None

            if wrapline:
                wrap_point=wrapline.startSketchPoint                              # We want the point really
                eprint('need code to pick correct center based on planes etc')
#                if not wrapstart.geometry.distanceTo(wrap_point.geometry) > 0:  # If we guessed the wrong end of their line, use the other
#                    wrap_point=wrapline.startSketchPoint                        # bottom is not the nose
                (wrapcx,wrapcy,wrapcz)=(wrap_point.geometry.x, wrap_point.geometry.y, wrap_point.geometry.z) # Center
                (wrappx,wrappy,wrappz)=(wrapstart.geometry.x, wrapstart.geometry.y, wrapstart.geometry.z)    # hub edge starting point
                #wrapcz=nose.geometry.x-tail.geometry.x # testing
                #radius=( (wrapcy-wrappy)**2 + (wrapcz-wrappz)**2 ) ** 0.5
                radius=wrap_point.geometry.distanceTo(join.geometry)
                #radius=join.geometry.z
                circumference=math.pi * 2 * radius
                x=splinex[i]*scale+nosex+shifto
                dist=(x-wrappx)/circumference * math.pi * 2 # How many radians do we need to rotate to match this distance around the circumference?
                #splinex[i]=  x * math.cos(dist) + z * math.sin(dist)
                #splinez[i]= -x * math.sin(dist) + z * math.cos(dist)
                splinex[i]=(( radius * math.sin(dist) ) - nosex-shifto) / scale # The last 2 just pre-un-do the scale/translate that's about to come next
                splinez[i]=  - radius * math.cos(dist)

            points.add(adsk.core.Point3D.create( splinex[i]*scale+nosex+shifto, spliney[i]*scale+nosey+shifto, splinez[i])) # caution - seems to auto-add constraints when my points hit other points. # +1 to prevent auto-constraining going on
            eprint("Added point {} at ({}, {}, {})  [spline was ({}, {})] shifted:{}".format(i,splinex[i]*scale+nosex, spliney[i]*scale+nosey, splinez[i], splinex[i],spliney[i],shifto))
            adsk.doEvents()


        #Generates the spline curve
        foilobj=sketch.sketchCurves.sketchFittedSplines.add(points) # Caution: auto-joins coincident points (the start and the end) dropping the duplicates.  $#foilobj==$#points-1

        # Constrain it now, working from the nose to the tail...
        if constrain:
            lasti=-1
            firstcname=None
            lastcname=None # for future re-calcs
            # Add driven chord, so we can tell later if it gets changed
            rh=dim.addDistanceDimension(nose, tail, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, pointme(tail.geometry,scale,'x',1), False) # False means driven
            firstcname=rh.parameter.name # how to set sizes if not driven: rh.parameter.expression='{} cm'.format(abs(nosex-tailx))
            rv=dim.addDistanceDimension(nose, tail, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, pointme(tail.geometry,scale,'y',1), False) # False means driven
            # Note also the CM in dimensions
            dim.addDistanceDimension(nose, cmpt, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, pointme(cmpt.geometry,scale,'x',1), True)
            dim.addDistanceDimension(nose, cmpt, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, pointme(cmpt.geometry,scale,'y',1), True)

            if (joindx or joindy) and not join.sketchDimensions.count:  # Constrain the CM, unless they already did themselves.
                rh=dim.addDistanceDimension(nose, join, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, pointme(join.geometry,scale,'x',0))
                rh.parameter.expression='{} cm'.format(abs(joindx))
                rv=dim.addDistanceDimension(nose, join, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, pointme(join.geometry,scale,'y',0))
                rv.parameter.expression='{} cm'.format(abs(joindy))

            for j in range(middle,len(splinex)): # Move along the undersurface from the nose to the tail
                for i in[j,middle+(middle-j)]:
                    if i==lasti: continue # Don't do nose twice
                    lasti=i 
                    if i<foilobj.fitPoints.count:
                        eprint("Constraining point {} at ({}, {})  [spline was ({}, {}), dimension was ({},{})]".format(i,splinex[i]*scale+nosex, spliney[i]*scale+nosey, splinex[i],spliney[i],  splinex[i]*scale,spliney[i]*scale))
                        sp=foilobj.fitPoints.item(i)
                        if shifto:
                            if splinex[i]<0 and spliney[i]<0:
                                sp.move( adsk.core.Vector3D.create(  -shifto, -shifto, 0.0 ))    # Can't have negative constraints, so put it where it goes now (hopefully that won't merge this point with any it now lands on!)
                            elif splinex[i]<0:
                                sp.move( adsk.core.Vector3D.create(  -shifto, 0.0, 0.0 )) # Leave Y alone
                            elif spliney[i]<0: 
                                sp.move( adsk.core.Vector3D.create(  0.0, -shifto, 0.0 ))   # Leave X alone
                        while (sp.sketchDimensions.count):
                            eprint('Caution: erased user constraint {}'.format(i))
                            try:
                                sp.sketchDimensions.item(0).deleteMe() # should never happen, but if our random-shift bumped exactly into something of the users, it might...
                            except:
                                eprint('Caution: user constraint erasure failed {}'.format(i))
                        try:
                            rh=dim.addDistanceDimension(nose, sp, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, pointme(sp.geometry,scale,'x',i==j))
                            rh.parameter.expression='{} cm'.format(abs(splinex[i]*scale))
                            if not firstcname: firstcname=rh.parameter.name # remember the first one we added
                        except:
                            eprint('Caution: add H constraint failed {}'.format(i))
                        try:
                            rv=dim.addDistanceDimension(nose, sp, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, pointme(sp.geometry,scale,'y',i==j))
                            rv.parameter.expression='{} cm'.format(abs(spliney[i]*scale))
                            lastcname=rv.parameter.name
                        except:
                            eprint('Caution: add V constraint failed {}'.format(i))
                        adsk.doEvents()
            sharejson['firstcname']=firstcname  # Constraint names - needed to perform re-calcs in future.
            sharejson['lastcname']=lastcname


        if endscale:
            shifto=0
            for j in range(middle+1,len(splinex)-1): # Move along the undersurface from the nose to the tail - note, range, never hits end...
                tweak=1-abs(j-( middle+1 + len(splinex) )/2) / len(splinex) # 0.5 to 1 to 0.5 - makes the middle 50% longer than the ends
                
                underpt=j
                underpt=adsk.core.Point3D.create( splinex[underpt]*scale+nosex+shifto, spliney[underpt]*scale+nosey+shifto, 0.0)
                overpt=middle+(middle-j)
                overpt=adsk.core.Point3D.create( splinex[overpt]*scale+nosex+shifto, spliney[overpt]*scale+nosey+shifto, 0.0)
                enddist=underpt.distanceTo(overpt) # Not the best plan - top and bottom surface points are not always in line, leading to screwey distances...
                endcap = adsk.core.ObjectCollection.create() 

                endcap.add(overpt)
                endcap.add(underpt)
                endline=sketch.sketchCurves.sketchLines
                endline.addByTwoPoints(underpt,overpt) # join the shape ends with a line, so the shape can be lofted

                if 1: # Testing slowness
                    minor=adsk.core.Point3D.create( 0.5*(overpt.x+underpt.x), 0.5*(overpt.y+underpt.y), endscale*enddist*tweak) # ellipse minor axis
                    midpt=minor
                    endcap.add(midpt)
                    center=adsk.core.Point3D.create( 0.5*(overpt.x+underpt.x), 0.5*(overpt.y+underpt.y), 0) # ellipse center
                    major=overpt
                    try:
                        ellipse=sketch.sketchCurves.sketchEllipses.add(center, major, minor)
                    except:
                        eprint('Caution: sketchEllipses.add failed')

                elif 0:
                    midpt=adsk.core.Point3D.create( 0.5*(overpt.x+underpt.x), 0.5*(overpt.y+underpt.y), .5*enddist) # 3D point
                    endcap.add(midpt)
                else:
                    for mida in ( 3, 14.4, 90, 158.4, 177 ): # 2%, 8%, 50%, 92%, 98% - so the spline ends are not at an angle
                        # nice ends require the fist spline points to be in line with the foil edge
                        if mida==3:      clamp=-3
                        elif mida==177:  clamp=3
                        else:            clamp=0
                        intpt=adsk.core.Point3D.create( 0.5*(1+math.cos(    (mida+clamp)/180*math.pi))*overpt.x+
                                                        0.5*(1+math.cos((180-mida-clamp)/180*math.pi))*underpt.x,
                                                        0.5*(1+math.cos(    (mida+clamp)/180*math.pi))*overpt.y+
                                                        0.5*(1+math.cos((180-mida-clamp)/180*math.pi))*underpt.y, 
                                                        0.5*math.sin(mida/180*math.pi)*enddist) # 3D point
                        endcap.add(intpt)
                        if mida==90: midpt=intpt 
                        adsk.doEvents()

                if j==middle+1:                                                 # join the nose too
                    endline=sketch.sketchCurves.sketchLines
                    endline.addByTwoPoints(midpt, adsk.core.Point3D.create( splinex[middle]*scale+nosex+shifto, spliney[middle]*scale+nosey+shifto, 0.0) )
                if j==len(splinex)-2:                                           # join the tail too
                    endline=sketch.sketchCurves.sketchLines
                    endline.addByTwoPoints(midpt, adsk.core.Point3D.create( splinex[0]*scale+nosex+shifto, spliney[0]*scale+nosey+shifto, 0.0) )

        sharejson['points']=points # So caller can add rails

        return sharejson    # Everything about what we just did

    # Error handling
    except:
        if textInfo:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox(program_name+' insert2DWing failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))
        return 'error'




def bestFoil(Re=None,N=None,strut=False,TextInfo=False):
    foilmatch=-1    # How close does the foil Re match our target Re?
    usefoil=None    # Which is the foil to use?
    foil=foildb2020.Foildb2020()    # Load the 1220 top candidates (filtered from 307M experiments) to search

    # See if we have data for the N we want - but if we do not find it, try either side until we do
    useN=0
    for noffs in range(0,11,1): # N goes from 3 to 14 (12 possible points) so the furthest from any we're on would be 11
        if useN: break
        for ntry in [N+noffs, N-noffs]: # does N+0 twice... boo hoo... should always be found first-go anyhow.
            if useN: break
            for tryfoil in foil:
                if ( tryfoil.get('n',0)==ntry                               # found at least one foil with this critical angle computed.
                    and ( (tryfoil.get('sym',1) < 0.00125 and strut)        # If it's symmetrical, and we want symmetrical, 
                    or (tryfoil.get('sym',1) >= 0.00125 and not strut))):   # or it's not symmetrical, and we want a wing (not symmetrical)
                    useN=ntry
                    break

    # Which database foil Re most closely-matches the one we want?
    for tryfoil in foil:
        if (tryfoil.get('n',0)!=useN                                        # Skip ones that do not apply to us...
            or (tryfoil.get('sym',1) < 0.00125 and not strut)               # If it's symmetrical, and we want a foil...
            or (tryfoil.get('sym',1) >= 0.00125 and strut)):                # or it's not symmetrical, and we want a strut
            continue # Skip the wrong ones
        dif=abs(Re - tryfoil.get('Re',0))
        if usefoil is None or dif<foilmatch:
            usefoil=tryfoil
            foilmatch=dif

    if foilmatch==Re: # foilmatch is 0 if perfect, Re if worst possible
        if TextInfo:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('Failed to find a foil to match your criteria - sorry!\n\nPlease use our forum/feedback link to report this problem')

    # Tell them about what we found
    goodness='' # CDp  =  CD - CDf
    if strut:
        goodness='drag coefficient: {:.5g} (=friction drag {:.5g} + pressure drag {:.5g})'.format(usefoil.get('CD','?'),usefoil.get('CDf','?'),usefoil.get('CDpres','?'))
    else:
        goodness='Best L/D={:.5g} at Aoa={:.5g} lift coefficient: {:.5g}, drag coefficient: {:.5g} (friction drag {:.5g} + pressure drag {:.5g})'.format(
            usefoil.get('CL',0) / usefoil.get('CD',1),
            usefoil.get('alpha','?'),
            usefoil.get('CL','?'),
            usefoil.get('CD','?'),
            usefoil.get('CDf','?'),
            usefoil.get('CDpres','?'))

    if TextInfo:
        #eprint("Best foil is a tested Re {:,.0f} n{} and named {}. {}".format(usefoil['Re'],useN,usefoil['Foil_fn'],goodness))
        vlog("Best foil is a tested Re {:,.0f} n{} and named {}. {}".format(usefoil['Re'],useN,usefoil['Foil_fn'],goodness))

    return usefoil



def insertTurbine( sketch=None,
                   nose=None,           # dlg['nose'+aft].selection(0).entity
                   tail=None,           # dlg['tail'+aft].selection(0).entity
                   join=None,
                   usefoil=None,        # from bestFoil()
                   rotate=None,    # <360 means they want best cl/cd auto-rotate applied
                   flip=None,      # Lift or downforce?
                   extrarotate=0, # Additional (on top of AoA, if any) rotation to apply (typically used for propeller pitch based on RPM, speed, and inflow)
                   wrapline=None,  # Center of a cylinder that the foil will be bent around
                   wrapstart=None, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not have to be part of the foil - only the X and distance-from-line is used.)
                   endscale=None,
                   textInfo=None,
                   constrain=None,
                   sharejson=None):     # Return info
    global VERSION,foilinfo

    try:

        (nosex,nosey,nosez)=(nose.geometry.x, nose.geometry.y, nose.geometry.z)
        (tailx,taily,tailz)=(tail.geometry.x, tail.geometry.y, tail.geometry.z)
        scale=nose.geometry.distanceTo(tail.geometry) # OK

        '''

        # Perform the insert
        insertTurbine( sketch=sketch, 
                    nose=nose,           # dlg['nose'+aft].selection(0).entity
                    tail=tail,           # dlg['tail'+aft].selection(0).entity
                    join=join,
                    usefoil=usefoil,
                    rotate=rotate,    
                    flip=flip,    
#                    extrarotate=0, # Additional (on top of AoA, if any) rotation to apply (typically used for propeller pitch based on RPM, speed, and inflow)
#                    wrapline=None,  # Center of a cylinder that the foil will be bent around
#                    wrapstart=None, # The point where the wrap will commence from (e.g. usually nose or tail or some middle area - does not have to be part of the foil - only the X and distance-from-line is used.)
                    endscale=endscale,
                    textInfo=True,      # Tell the user what we did in the text info area (and, for errors, with UI popups)
                    constrain=constrain,
                    sharejson=sharejson) 


        '''

    except:
        pass


# put dimensions into user-firendly non-overlapping spots
def pointme(dimpt,scale,xy,topbot):
    amt=scale/400
    newx=dimpt.x
    newy=dimpt.y
    if xy=='x':
        if topbot: # bottom
            newy=newy-amt
            newx=newx+amt
        else:
            newy=newy+amt/2
            newx=newx+amt
    else:
        if topbot: # bottom
            newy=newy+amt/2
            newx=newx-amt
        else:
            newx=newx-amt
    return adsk.core.Point3D.create(newx, newy, 0)

def xy_to_points(x,y):
    points=[]
    for i in range(0,len(x)):
        points.append(x[i])
        points.append(y[i])
    return points

def points_to_xy(points):
    (x,y)=([],[])
    for i in range(1,len(points)+1,2):
        x.append(points[i-1])
        y.append(points[i])
    return (x,y)



# Check to see if they changed something (e.g. chord len or parameter) that would require us to re-compute any foils...
class CommandHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self, targetCommand):
        super().__init__()
        self.tgtCmd = targetCommand
    def notify(self, args):
        global _ui
        try:
            web_nbreq(None) # Service non-blocking websocket
            # Possible things to watch...: FusionDragSketchCommand SketchEditDimensionCmdDef SketchDimension ChangeParameterCommand
            pass
#            if _ui.activeCommand == self.tgtCmd:
#                # Here, the change of UserParameters is checked.
#                _ui.messageBox('call ' + self.tgtCmd)
#            if debug:
#                eprint(_ui.activeCommand)

        except:
            pass



# Trigger a co-process to see if any updates exist, and get them if yes
def check_update(forcechk):
    ui = None
    try:
        global debug, VERSION, userdata, updatedata

        updatedata=load_user_settings(update_file)                  # Check any old previously-loaded update info
        if updatedata.get('loaded',0):                              # e.g. /Users/cnd/Library/Application Support/Airfoil_Tools/latest_version_aft.json or  C:\Users\cnd\AppData\Roaming\Airfoil_Tools\latest_version_aft.json
            updatedata['old']=True                                  # So we know the difference between old update info, and new stuff
        updatedata['loaded']=False

        # If not checked for updates before, or, last check was 23+ hours ago...
        if forcechk or ( not updatedata.get('last_check_time',0) ) or updatedata['last_check_time']+(23*60*60) < (int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())):
            # Start an update check, in the background, so it doesn't slow the user down. See home_file for where this gets written to
            try: # Writes JSON data into file latest_version'+aft+'.json in appropriate user settings folder
                eprint("backgrounding update-check into " + home_file(program_name,'.'))
                #r=subprocess.Popen([get_exec(),os.path.join(prog_folder,"check_update.py"),str(VERSION) + foildb2020.VERSION(VERSION) ,aft,program_name.replace(" ", "_")])
                #r=subprocess.Popen([get_exec(),os.path.join(prog_folder,"check_update.py"),str(VERSION) + "&db=" + str(foildb2020.VERSION(0)) ,aft,program_name.replace(" ", "_"),str(forcechk)])
                r=subprocess.Popen([get_exec(),os.path.join(prog_folder,"check_update.py"), str(VERSION) , aft, program_name.replace(" ", "_"), str(foildb2020.VERSION(0)), str(forcechk+2)])
            except:
                eprint('subprocess failed {}'.format(traceback.format_exc()))
                try:    # see if the path magically finds it
                    #r=subprocess.Popen(['python',os.path.join("prog_folder","check_update.py"),str(VERSION) + foildb2020.VERSION(VERSION) ,aft,program_name.replace(" ", "_")])
                    #r=subprocess.Popen(['python',os.path.join("prog_folder","check_update.py"),str(VERSION) + "&db=" + str(foildb2020.VERSION(0)) ,aft,program_name.replace(" ", "_"),str(forcechk+2)])
                    r=subprocess.Popen(['python',os.path.join("prog_folder","check_update.py"), str(VERSION) , aft, program_name.replace(" ", "_"), str(foildb2020.VERSION(0)), str(forcechk+2)])
                except:
                    eprint('subprocess failed again {}'.format(traceback.format_exc()))

    except:
        eprint("update-check problem")



#################################################################################
####                                                                          ###
##                               Main() Entry Point                            ##
####                                                                          ###
#################################################################################

def run(context):
    ui = None
    try:
        global textpalette, debug, VERSION, userdata, updatedata, pnl, _ui
        app = adsk.core.Application.get()
        _ui = app.userInterface
        ui = app.userInterface

        textpalette=ui.palettes.itemById('TextCommands')
        #welcome="Welcome to " + program_name + " Add-in v"+str(VERSION)+' ' + foildb2020.VERSION(VERSION)+" on " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z%z") + " (" + str(int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())) + ")"
        #welcome='Welcome to {} Add-in v{:1.8f}{} on {} ({})'.format(program_name, VERSION, foildb2020.VERSION(VERSION), datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z%z"), int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()))
        welcome='Welcome to {} Add-in v{:1.8f}{} on {}'.format(program_name, VERSION, foildb2020.VERSION(VERSION), datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z%z") )
        eprint(welcome) # eprint only prints in debug mode

        if  textpalette:
#            textpalette_ori_state=textpalette.isVisible
#            if debug:
#                textpalette.isVisible=True
            if textpalette.isVisible:
                textpalette.writeText(welcome) # So any logs we get from customers identify what and when

        check_update(0)

        if updatedata.get('critical',0):                            # Note that this flag was read from the result of an update that happened earlier (not the above in this run)
            ui.messageBox(updatedata['critical'])                   # Same as fatal, but allows our update code to run allowing the possible clearing of this problem
            # Need to backup user settings first...
            sys.exit(1)                                             # quit to prevent catastrophe (e.g. data corruption or security issue)


        #################################################################################
        ####                                                                          ###
        ##        Menu builder (for Button and DropDown (slide-out) UI elements)       ##
        ####                                                                          ###
        #################################################################################

        #ctrl => parent
        #  cmd => button inside ctrl
        #  def => assets for cmd (and, if promoted, ctrl buttons)
        def aft_make_ui(ui,onCommandCreated,aftid,mywhere,parentwhere,pctrl):                            # Add a command onto the Create menu in the Sketch workspace (toolbar panel)
            global uiel, handlers, userdata
            myui=uiel[aftid]    # this is a reference
            (myctrl,mycmd,mydef,mycb,myid)=( myui['ctrl'], myui['cmd'], myui['def'], myui['cb'], mywhere + '_' + myui['id'] ) # indexed by mywhere, so same commands can go on many menus
            newcmd=False # Is this a menu item that needs a new command handler for itself?
            if not onCommandCreated:
                newcmd=True

            if (myui['type'] == 'Command') or (myui['type'] == 'DropDown'):  # SolidCreatePanel / SketchCreatePanel
                newcmd=True

            if newcmd:
                onCommandCreated = CommandCreatedEventHandlerPanel({'aftid':aftid,'mywhere':mywhere}) # Instantiate the handler new object - we use just one for everything
                handlers.append(onCommandCreated)


            if myui['type'] == 'Button':                                                # Add a button to their tools menu
                mycmd[mywhere] = ui.workspaces.itemById('FusionSolidEnvironment').toolbarPanels.add(myui['id'],  myui["name"], mywhere, False) # SelectPanel

                # Recursive call to aft_make_ui to build all the commands we want to add on to our button
                done_icon=False
                for menu_item in uiel_order:
                    if menu_item:                                                       # Skip not-yet-defined menu stuff
                        subui=uiel[menu_item]
                        if (subui['type'] == 'Command') or (subui['type'] == 'Separator'):
                            aft_make_ui(ui,onCommandCreated,menu_item,myui['id'],mywhere,None)           # Add a command onto the Create menu in the Soild workspace
                            if not done_icon:
                                cmdControl :adsk.core.CommandControl = subui['cmd'][myui['id']] # Put an icon onto the button
                                cmdControl.isPromotedByDefault = True
                                done_icon=True

            elif (myui['type'] == 'Command') or (myui['type'] == 'Separator') or (myui['type'] == 'DropDown'):  # SolidCreatePanel / SketchCreatePanel
                if not pctrl:                                                           # If not, it's a fusion360 control, so go find the object
                    myctrl[mywhere]=ui.workspaces.itemById('FusionSolidEnvironment').toolbarPanels.itemById(mywhere)
                else:
                    if not myctrl.get('mywhere',0):
                        myctrl[mywhere]=pctrl                                           # The control is our parent if we have one
                        newcmd=True

                if not myctrl[mywhere]:
                    myctrl[mywhere]=ui.workspaces.itemById('FusionSolidEnvironment').toolbarPanels.itemById(mywhere).controls.itemById(myui['id'])

                if myctrl[mywhere].controls.itemById(myui['id']):
                    ui.messageBox('Sorry!  We detected an unclean-shutdown from ' + program_name + '.  You may need to save your work, then quit and restart Fusion 360 to correct.\n\n'+
                                  'If this message appears again, disable "Run on Startup" for ' + program_name + ' from your Tools => Add-ins menu')
                    # We could in theory search all menus and panels for lal our IDs here if we want... but this should never happen anyway.

                if(myui['type'] == 'Separator'):                                        # Add a button to their tools menu
                    mycmd[mywhere]=myctrl[mywhere].controls.addSeparator(myui['id'])    # (id, positionID, isBefore)
                    myui['name']='-----------'                                          # So the debug messagebox works

                elif(myui['type'] == 'DropDown'):                                       # Add a right-sliding list of commands to their dropdown
                    mycmd[mywhere] = myctrl[mywhere].controls.addDropDown(myui['name'], myui['res'], myui['id'], insertIndex(aftid,mywhere), False) # False means after

                    # Recursive call to aft_make_ui to build all the commands we want to add on to our button
                    for menu_item in uiel_order:
                        if menu_item:                                                   # Skip not-yet-defined menu stuff
                            subui=uiel[menu_item]
                            if (subui['type'] == 'Command') or (subui['type'] == 'Separator'):
                                aft_make_ui(ui,onCommandCreated,menu_item,myui['id'],mywhere,mycmd[mywhere])     # Add a command onto the Create menu in the Soild workspace
                    mycmd[mywhere].isVisible = True

                else:   # Command
                    mydef[mywhere]=ui.commandDefinitions.itemById(myid)                 # Already done'id'
                    if not mydef[mywhere]:
                        altid={} # use alternate versions of this command's assets for this specific sub menu
                        for tryid in ('name','desc','html','res','abs_res'):            # Things that can look different when this command appears in different sub menus
                            for myparent in ('.'+mywhere, '.'+parentwhere, ''):
                                if myui.get(tryid+myparent,0):                          # Different name for items in this specific parent
                                    altid[tryid]=myui[tryid+myparent]
                                    break
                        mydef[mywhere] = ui.commandDefinitions.addButtonDefinition(myid, altid['name'], altid['desc'], altid['res'])
                        mydef[mywhere].toolClipFilename = make_html(myui['id'],altid)   # Clips cannot be relative-positioned files        
                        if myui.get('tip',0):
                            mydef[mywhere].tooltip = myui['tip']
                        #mycb[mywhere]=CommandCreatedEventHandlerPanel(ui,aftid,mywhere,myparent,altid.copy()) # Instantiate the handler new object - and in myui(uiel).cb thus keeps the handler referenced beyond this function
                        mydef[mywhere].commandCreated.add(onCommandCreated)              # Link our handler to the new definition
                    else:
                        dome=False

                    mycmd[mywhere]=myctrl[mywhere].controls.addCommand(mydef[mywhere])  # Add the command referencing this definition to the menu
                    mycmd[mywhere].isVisible = True
            else:
                if userdata["debug"]:
                    ui.messageBox(program_name + ' unknown type:' + myui['type'])

            return myui # Give caller everything so they can use what they like




        #################################################################################

        class MyCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler): # Only called if all needed points are selected
            def __init__(self, pnlid):
                global userdata
                super().__init__() # need to store our dialogue id in here...
                self.pnlid=pnlid        # So we know which menu-item/button triggered us
                #if userdata["debug"]:
                    #eprint("init MyCommandValidateInputsHandler()\n")
                    #eprint("init InputChangedHandler("+pnlid+")\n")
            def notify(self, args):
                # areInputsValid    Used during the AreInputsValid event to get or set if all inputs are valid and the OK button should be enabled.
                # firingEvent       The event that the firing is in response to.
                # inputsu           Returns the collection of command inputs that are associated with the command this event is being fired for.
                #    adsk.core.ValidateInputsEventArgs.cast(args)  .firingEvent.sender.commandInputs
                try:
                    eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
                    inputs = eventArgs.firingEvent.sender.commandInputs        

                    ret=MyValidate(self.pnlid,eventArgs,inputs,'validate') # Same code does Validate and Change events
                    args.areInputsValid=ret
                    return ret
                except:
                    eprint('MyCommandValidateInputsHandler failed {}'.format(traceback.format_exc()))




        #################################################################################

        class InputChangedHandler(adsk.core.InputChangedEventHandler):
            def __init__(self, pnlid):
                super().__init__()
                self.pnlid=pnlid        # So we know which menu-item/button triggered us
            def notify(self, args):
                global pnl,debug
                #command = args.firingEvent.sender
                try:
                    eventArgs = adsk.core.InputChangedEventArgs.cast(args)
                    inputs=eventArgs.inputs

                    #ret=MyValidate(self.pnlid,None,None,self,args) # Same code does Validate and Change events
                    ret=MyValidate(self.pnlid,eventArgs,inputs,'changed') # Same code does Validate and Change and Command events
                    args.areInputsValid=ret
                    return ret
                except:
                    eprint('InputChangedHandler failed: {}'.format(traceback.format_exc()))


        #################################################################################

        class CommandExecuteHandler(adsk.core.CommandEventHandler):
            def __init__(self, pnlid):
                super().__init__()
                self.pnlid=pnlid        # So we know which menu-item/button triggered us
            def notify(self, args):
                try:
                    eventArgs = adsk.core.CommandEventArgs.cast(args)
                    inputs = eventArgs.command.commandInputs        

                    ret=MyValidate(self.pnlid,eventArgs,inputs,'execute') # Same code does Validate and Change and Execute events

                    if ret: # A valid foil
                        if self.pnlid.get('aftid')=='create_turbine'+aft:
                            insertTurbineUI(self.pnlid,args,inputs)
                        else:
                            insert2DWing(self.pnlid,args,inputs)

                except:
                    app = adsk.core.Application.get()
                    ui = app.userInterface
                    if ui:
                        ui.messageBox(program_name+' cmd exec failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))


        #################################################################################

        class ExecutePreviewHandler(adsk.core.CommandEventHandler):
            def __init__(self, pnlid):
                super().__init__()
                self.pnlid=pnlid        # So we know which menu-item/button triggered us
            def notify(self, args):
                try:
                    eventArgs = adsk.core.CommandEventArgs.cast(args)   # args.firingEvent.sender
                    inputs = eventArgs.command.commandInputs            # 

                    ret=MyValidate(self.pnlid,eventArgs,inputs,'preview') # Same code does Validate and Change and Execute and preview events

                    if ret: # A valid foil
                        pass
                    eprint('ExecutePreviewHandler called')

                except:
                    eprint('ExecutePreviewHandler failed: {}'.format(traceback.format_exc()))

        #################################################################################

        class CommandCreatedEventHandlerPanel(adsk.core.CommandCreatedEventHandler):
            def __init__(self, pnlid):
                super().__init__() 
                self.pnlid=pnlid        # So we know which menu-item/button triggered us
            def notify(self, args):
                global userdata, updatedata, pnl
                try:
                    eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
                    cmd = eventArgs.command
                    #inputs = cmd.commandInputs
                    #cmd = args.command
                    #cmd = adsk.core.Command.cast(args.command)
                    nospacehelpfn='/tmp/help.html'
                    if os.path.isfile(nospacehelpfn):
                        cmd.helpFile = nospacehelpfn                                         # Works! - everything else with spaces in the path always fails.


                    onExecute = CommandExecuteHandler(self.pnlid)
                    cmd.execute.add(onExecute)
                    handlers.append(onExecute)

                    onInputChanged = InputChangedHandler(self.pnlid)
                    cmd.inputChanged.add(onInputChanged)
                    handlers.append(onInputChanged) # keep the handler referenced beyond this function

                    onValidate = MyCommandValidateInputsHandler(self.pnlid) # (self.ui,self.pnlid)
                    cmd.validateInputs.add(onValidate)
                    handlers.append(onValidate)                                         # keep the handler referenced beyond this function

                    onPreview = ExecutePreviewHandler(self.pnlid)
                    cmd.executePreview.add(onPreview)
                    handlers.append(onPreview)

                    #onDestroy = MyCommandDestroyHandler()                      # We are an add-in (we stick around) - see the stop() which always gets called when we re unloaded though

                    updatedata=load_user_settings(update_file)                  # Check results from our earlier update check now, so our panel knows if it needs to tell the user about updates

                    p=aft_make_dlg(cmd,self.pnlid) 
                    pnl['opened']=int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())
                    pnl['openc']=pnl['openc']+1
                    if updates(True): # check only
                        pnl[p]['update_now'+aft].isVisible=True

                except:
                    if ui:
                        ui.messageBox(program_name+' panel create failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))


        #################################################################################

        if userdata.get("firstrun",1):
            if userdata.get("release",1):
                ui.messageBox(program_name + ' is added in these 2 places:\n\n' +
                                            '*  The Create menu dropdown in your Sketch\n'+
                                            '     workspace\n' +
                                            '*  A button in your "Tools" tool bar panel\n\n' +
                                            '             This is a one-time message.\n' +
                                            '             We hope you love our add-in.','Welcome to '+program_name)
            else:
                ui.messageBox(program_name + ' is added in these 3 places:\n\n' +
                                            '*  The Create menu dropdown in your Sketch\n'+
                                            '     workspace\n' +
                                            '*  The Create menu dropdown in your Solid Design\n' +
                                            '     workspace\n' +
                                            '*  Your "Tools" tool bar panel\n\n' +
                                            '             This is a one-time message.\n' +
                                            '             We hope you love our add-in.','Welcome to '+program_name)
            userdata["firstrun"]=False
            userdata["debug"]=False
            userdata["unsaved"]=True
            userdata["release"]=True
            save_user_settings(ui,settings_file)                                # Bug them about how to run/use/find this just one time

        aft_make_ui(ui,None,'sketch_airfoil_command'+aft,'SketchCreatePanel',None,None)   # Add a command onto the Create menu in the Sketch workspace
        if userdata.get("debug",0): aft_make_ui(ui,None,'solid_airfoil_command'+aft,'SolidCreatePanel',None,None)     # Add a command onto the Create menu in the Soild workspace
        aft_make_ui(ui,None,'airfoil_toolbar_button'+aft,'SelectPanel',None,None)         # Add a button to their Tools menu - if this is last, it works.

        if userdata.get("debug",0):
            debug=True
            ui.messageBox(program_name + ' started.\n\nIf you see this message in error, edit the debug flag to false in this file:-\n\n' + home_file(program_name,settings_file))

        # link in to check if they change anyting that affects a foil we inserted
        pnl['onCommand'] = CommandHandler('ChangeParameterCommand')
        ui.commandTerminated.add(pnl['onCommand']) # Also services any non-blocking sockets.

    except:
        if ui:
            ui.messageBox(program_name+' AddIn start failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))
        eprint('AddIn Start Failed: {}'.format(traceback.format_exc())) # ?vlog?



#################################################################################
####                                                                          ###
##                                  The End                                    ##
####                                                                          ###
#################################################################################

def stop(context):                                                              # Runs when we get unloaded
    global userdata, pnl
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

#        if textpalette:                                                         # Put it back how it was, so the View=>TextCommands master window which says "Show" or "Hide" matches the state OK)
#            try:
#                textpalette.isVisible = textpalette_ori_state
#            except:
#                pass

        if userdata.get('unsaved',1):
            save_user_settings(ui,settings_file)                                # Bug them about how to run/use/find this just one time

        # Go through all our handlers and run the deleteMe() on them now...
        for aftid in uiel:                                                      # Every menu item
            myui=uiel[aftid]
            for mywhere in myui['cmd']:                                         # Every place it's used in a command
                if myui['cmd'][mywhere]:
                    try:
                        myui['cmd'][mywhere].deleteMe()
                    except:
                        pass
                myui['cmd'][mywhere]=None
            for mywhere in myui['def']:                                         # Every definition too
                if myui['def'][mywhere]:
                    try:
                        myui['def'][mywhere].deleteMe()
                    except:
                        pass
                myui['def'][mywhere]=None

        if pnl.get('onCommand',0): 
            ui.commandTerminated.remove(pnl['onCommand'])
            pnl.clear()

        if debug:
            ui.messageBox(program_name + ' ended.\n\nIf you see this message in error, edit the debug flag to false in this file:-\n\n' + home_file(program_name,settings_file))

    except:
        if ui:
            ui.messageBox(program_name+' stop cmd failed: please send us a screenshot of this:\n{}'.format(traceback.format_exc()))
        eprint(program_name + ' STOP command failed:\n{}'.format(traceback.format_exc()))



#################################################################################
####                                                                          ###
##                             Helper functions                                ##
####                                                                          ###
#################################################################################

def eprint(*args, **kwargs):                                                    # Print debug stuff to STDOUT
    global debug
    if debug:
        print(*args, file=sys.stderr, **kwargs)

def nextId():                                                                   # Add sequential order to my UI command dictionary
    global panelorder
    panelorder=panelorder+1
    return panelorder

# Find a cross-platform friendly and appropriate place to save user settings files (see also the main program which does this same thing)
def home_file(program_name,settings_filename):
    if sys.platform.startswith('linux'):
        home_folder='~/.local/share'                                            # ~/.local/share/<AppName>
    elif sys.platform.startswith('darwin'):
        home_folder='~/Library/Application Support/'                            # ~/Library/Application Support/<AppName>
    else:
        home_folder=os.path.join('~','AppData','Roaming')                       # C:\Users\cnd\AppData\Roaming

    home_folder=os.path.expanduser(os.path.join(home_folder,program_name.replace(" ", "_")))
    os.makedirs(home_folder, exist_ok=True)
    return os.path.join(home_folder,settings_filename)

def load_user_settings(settings_file_only):                                     # Read user settings, like firstrun flag, units, history, helpers, etc
    settings_file=home_file(program_name,settings_file_only)                    # Put this in the correct user home folder
    try:
        with open(settings_file,'r', newline='\n', encoding='utf-8' ) as json_file:
            udata = json.load(json_file)
        udata['loaded']=True
    except:
        udata={"firstrun":True}
    return udata

def save_other_settings(settings_file_only,tosave):                             # Save the settings (update file usually)
    settings_file=home_file(program_name,settings_file_only)                    # Put this in the correct user home folder
    try:
        with open(settings_file,'w', newline='\n', encoding='utf-8') as json_file:
            json_file.write(json.dumps(tosave)+"\n")
            json_file.close()
    except:
        pass

def save_user_settings(ui,settings_file_only):                                  # Save the settings that we want to remember between sessions etc.
    global userdata
    settings_file=home_file(program_name,settings_file_only)                    # Put this in the correct user home folder
    try:
        with open(settings_file,'w', newline='\n', encoding='utf-8') as json_file:
            userdata["unsaved"]=False
            json_file.write(json.dumps(userdata)+"\n")
            json_file.close()
    except:
        if ui:
            userdata["unsaved"]=True
            ui.messageBox('Problem writing user settings save file: ' + settings_file)




def foiltool(ui,settings_file,mywork):                                          # Call our core processor to perform specified work
    cmdname=prog_folder+'/airperl.pl'
    forperl = "For Perl! path='" + os.path.dirname(os.path.realpath(__file__)) + "'\n"

    try:
        r=subprocess.run([foiltool, '-l', '/dev/null'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         check=True,
                         universal_newlines=True,
                         input=forperl)
        ui.messageBox(r.stdout)

    except Exception as e:
        ui.messageBox(e)


def make_html(myid,altid):
    global clipa, clipb
    if altid.get('html',0):                                                     # toolClip help text exists: put it into a file for Fusion360 to use right now:
        clipfn=os.path.join(altid['abs_res'], myid + '.html')
        try:
            f=open(clipfn,'w')
            f.write(clipa+altid['html']+clipb)                                  # Add required template HTML around our toolClip help text.
            f.close()
            return clipfn
        except:
            eprint("Error writing toolClip output html file '"+clipfn+"':\n\n{}".format(traceback.format_exc()))
    return ''


def insertIndex(aftid,mywhere):                                                 # Return the string to place our command in the right place, if we asked for it
    myui=uiel[aftid] # this is a reference
    if myui.get('after',0): # If we have defined a lits of things, one of which we want to appear after...
        for pnlid in myui['after']: # Search for one
            insertAfter = myui['ctrl'][mywhere].controls.itemById(pnlid) # Does this exist?
            if insertAfter: # yes
                return pnlid # insert after this then
    return ''


def distance_between_two_points(frompt,topt):                                   # ... in 3D
    if frompt and topt:
        return (   ( frompt.point.x - topt.point.x )**2 + \
                   ( frompt.point.y - topt.point.y )**2 + \
                   ( frompt.point.z - topt.point.z )**2 \
                            ) ** 0.5
    return 0.0

def vlog(*args, **kwargs):                                                     # Print runtime stuff to the Fusion360 TextCommands palette area
    global textpalette, userdata
    if not userdata.get('disable_vlog',0):
        if textpalette:
            pstr = io.StringIO()
            print(*args, file=pstr, end = '', **kwargs)
            textpalette.writeText(pstr.getvalue()) 
            pstr.close()
        if debug:
            print(*args, file=sys.stderr, **kwargs)


def C_to_Rankine(C):                                                            # temperature converter; Rankine is the imperial Farenheight version of K
    #0^C * 9/5 + 491.67 = 491.67^R
    return C * 9/5 + 491.67

def Gas_Viscosity(gas,tempC):                                                    # Return the dynamic viscosity in centipoise for a gas at the given temperature
    #https://www.lmnoeng.com/Flow/GasViscosity.php
    #Sutherland's constant C  /  To (oR)  /  ?o (centipoise)
    constant= { 'Air':{'C':120, 'T0':524.07, 'U0':0.01827}, #   standard air
                'NH3':{'C':370, 'T0':527.67, 'U0':0.00982}, #   ammonia, NH3
                'CO2':{'C':240, 'T0':527.67, 'U0':0.01480}, #   carbon dioxide, CO2
                'CO': {'C':118, 'T0':518.67, 'U0':0.01720}, #   carbon monoxide, CO
                'H2': {'C':72,  'T0':528.93, 'U0':0.00876}, #   hydrogen, H2
                'N2': {'C':111, 'T0':540.99, 'U0':0.01781}, #   nitrogen, N2
                'O2': {'C':127, 'T0':526.05, 'U0':0.02018}, #   oxygen, O2
                'SO2':{'C':416, 'T0':528.57, 'U0':0.01254}} #   sulfur dioxide, SO2
    # Gas viscosity is computed using Sutherland's formula (Crane, 1988):
    # ? = ?o*(a/b)*(T/To)3/2

    # a = 0.555To + C
    # b = 0.555T + C

    #   where
    # ?  = viscosity in centipoise at input temperature T�R
    # ?o = reference viscosity in centipoise at reference temperature To�R
    # T   = input temperature in degrees Rankine
    # To = reference temperature in degrees Rankine
    # C  = Sutherland's constant

    T=C_to_Rankine(tempC)
    a = 0.555 * constant[gas]['T0'] + constant[gas]['C'] 
    b = 0.555 * T + constant[gas]['C']
     
    u = constant[gas]['U0'] * (a/b) * ( T / constant[gas]['T0'] ) ** (3/2)
    
    return u/1000                                                               # dynamic viscosity in centipoise at input temperature T�C

def Water_Density(fluid,tempC):                                           # Return the density in kg/m� of water at the given temp (C) 
    if tempC < 126.85:
        p =  (-9.204453627E-11 * tempC**4 +3.420742008672E-8* tempC**3 -7.08919807166417E-6* tempC**2 +4.375294545181970E-5* tempC +0.999888264405735)*1000
    else:
        p = (-6.7028E-15* tempC**6 +8.28885789E-12* tempC**5 -4.18617351813E-9* tempC**4 +1.0964248668453E-6* tempC**3 -1.58525167407245E-4* tempC**2 +0.0111966695465985* tempC +0.669696280822552)*1000

    if fluid == 'Fresh Water':
        return p
    elif fluid == 'Sea Water':
        return Water_Density('Fresh Water',tempC*1.0278+4)+27.69924894   # Scale sea based on fresh
    else:       # Any water
        return 0.5 * ( p + Water_Density('Fresh Water',tempC*1.0278+4)+27.69924894 )  # Midway between them both...


def Water_Viscosity(tempC):                                           # Return the viscosity of water in Pa.s
    T=273.15+tempC
    A=2.414E-5
    B=247.8
    C=140
    v = A * 10**(B/(T-C))
    return v


def Fluid_Viscosity(fluid): # Not temp dependent
    #http://www-mdp.eng.cam.ac.uk/web/library/enginfo/aerothermal_dvd_only/aero/fprops/propsoffluids/node5.html
    # The viscosity of air depends mostly on the temperature. At 15 �C, the viscosity of air is 1.81 � 10-5 kg/(m�s) , 18.1 ?Pa�s or 1.81 � 10-5 Pa�s .
    # The kinematic viscosity of air at 15 �C is 1.48 � 10-5 m2 /s or 14.8 cSt. At 25 �C, the viscosity is 18.6 ?Pa�s and the kinematic viscosity 15.7 cSt.
    # https://www.translatorscafe.com/unit-converter/en-US/calculator/altitude/#altidude-scheme-big
    pass

'''
def Density(gas,tempC,pressurePa):                                              # Return the density in kg/m� of air at the given temp (C) and pressure (Pa)
    if gas[-5:] == 'Water': # All 3 that end with "Water"
        dense0=None
        if gas == 'Fresh Water':
            dense0=1000.0
        else:
            dense0=1028.1685    # Sea at 0C from https://ittc.info/media/4048/75-02-01-03.pdf

        A=0.14395
        B=0.0112 
        C=649.727 
        D=0.05107 
        Tmin=273 
        Tmax=648

        p= A / ( B ** (1+ ( 1 - (tempC-273.15)/C )**D ) )    # http://ddbonline.ddbst.de/DIPPR105DensityCalculation/DIPPR105CalculationCGI.exe?component=Water
        return p

    elif gas != 'Air':
        # The molar mass of dry air is 28.9647 g/mol
        # The gas constant R is 8.314 J / mol�K. 
        # Rsp = 287.052 J�kg?��K?� 
        #   where
        # p is the absolute pressure in Pa,
        # T is the absolute temperature of air in K, and

        # P = p/(Rsp.T)
        P = pressurePa / 287.052 * (273.15+tempC)
        return P
    else:
        raise Exception("This is only for air at present")

    return None

'''

def Altitude_to_Pressure(h): # Alt in meters above sea level, returns Pa
    # See https://en.wikipedia.org/wiki/Barometric_formula
    # Tested on https://www.digitaldutch.com/atmoscalc/
    # Test; 0=101.32, 1=89.876, 7=41.105, 11=22.7, 15=12.112, 20=5.529, 25=2.549, 32=8.89m ,40=2.871, 47=1.158, 49=90.327Pa, 51=70.45, 60=21.955, 71=4.478, 75=2.387, 84=0.531, 85.5=0.408

    # height asl: h(m)  mass density: p(kg/m^3) standard temp: T(K)   temp lapse rate: L(K/m)
    table=[{'b':0,   'h':0,     'hto':11000,  'P':101325,   'T':288.15,  'L':-0.0065   },
           {'b':1,   'h':11000, 'hto':20000,  'P':22632.06,  'T':216.65,  'L':0.0       },
           {'b':2,   'h':20000, 'hto':32000,  'P':5474.889,  'T':216.65,  'L':0.001     },
           {'b':3,   'h':32000, 'hto':47000,  'P':868.0187,  'T':228.65,  'L':0.0028    },
           {'b':4,   'h':47000, 'hto':51000,  'P':110.9063,  'T':270.65,  'L':0.0       },
           {'b':5,   'h':51000, 'hto':71000,  'P':66.93887,  'T':270.65,  'L':-0.0028   },
           {'b':6,   'h':71000, 'hto':999999, 'P':3.95642, 'T':214.65,  'L':-0.002    }]

    for layer in table: # Find the line we want
        if h >= layer['h'] and h < layer['hto']:
            break

    R=8.3144598 # N�m/(mol�K) universal gas constant 
    g0=9.80665  # m/s2          gravity
    M=0.0289644 # kg/mol        molar mass of Earth's air

    if layer['L']: # Formula 1
        p = layer['P'] * ( layer['T'] / (layer['T']+layer['L']*(h-layer['h'])) )**( (g0*M)/(R*layer['L']) )
    else: # Formula 2
        p = layer['P'] * math.exp( ( -g0*M*(h-layer['h']) ) / ( R * layer['T']  ) )

    return p

def Altitude_to_Density(h): # Alt in meters about sea level, returns kg/m^3 
    # See https://en.wikipedia.org/wiki/Barometric_formula
    # Tested on https://www.digitaldutch.com/atmoscalc/

    # height asl: h(m)  mass density: p(kg/m^3) standard temp: T(K)   temp lapse rate: L(K/m)
    table=[{'b':0,   'h':0,     'hto':11000,  'p':1.2250,   'T':288.15,  'L':-0.0065   },
           {'b':1,   'h':11000, 'hto':20000,  'p':0.36391,  'T':216.65,  'L':0.0       },
           {'b':2,   'h':20000, 'hto':32000,  'p':0.08803,  'T':216.65,  'L':0.001     },
           {'b':3,   'h':32000, 'hto':47000,  'p':0.01322,  'T':228.65,  'L':0.0028    },
           {'b':4,   'h':47000, 'hto':51000,  'p':0.00143,  'T':270.65,  'L':0.0       },
           {'b':5,   'h':51000, 'hto':71000,  'p':0.00086,  'T':270.65,  'L':-0.0028   },
           {'b':6,   'h':71000, 'hto':999999, 'p':0.000064, 'T':214.65,  'L':-0.002    }]

    for layer in table: # Find the line we want
        if h >= layer['h'] and h < layer['hto']:
            break

    R=8.3144598 # N�m/(mol�K) universal gas constant 
    g0=9.80665  # m/s2          gravity
    M=0.0289644 # kg/mol        molar mass of Earth's air

    if layer['L']: # Formula 1
        p = layer['p'] * ( layer['T'] / (layer['T']+layer['L']*(h-layer['h'])) )**( 1 + (g0*M)/(R*layer['L']) )
    else: # Formula 2
        p = layer['p'] * math.exp( ( -g0*M*(h-layer['h']) ) / ( R * layer['T']  ) )

    return p


def getReV(dens,kvisc,L,s,h):    # Length in meters, s in meters per second, height in meters
    return dens * s * L / kvisc          # Reynolds number

def getRe(medium,L,s,h,tempC):    # Length in meters, s in meters per second, height in meters
    if medium[-5:] == 'Water': # All 3 that end with "Water"
        Re=Water_Density(medium,tempC) * s * L / Water_Viscosity(tempC)         # Reynolds number
    else:
        Re=Altitude_to_Density(h) * s * L / Gas_Viscosity(medium,tempC)         # Reynolds number
    return Re

def Kv(gas,L,s,h,tempC):    # Length in meters, s in meters per second, height in meters
    kv=Gas_Viscosity(gas,tempC) / Altitude_to_Density(h)                        # kinematic viscosity
    return kv

# Do a J-Spline, with facility to handle ending points properly as well (or do loops too)
def jspline(sl, a, b, link, pts):                                               # link=0 (join), 1 (simple clamp), 2 (tangent clamp), or 3 (loop)
    ret=[]                                                                      # sl usually ~ 5.  a=b=1 for b-spline, a=b=0 for 4-point subdiv, etc
    for px in pts:              
        x=px.copy()                                                             # Where the spline gets built
        k=0                                     
        while k < sl:
            k=k+1                               
            if link==1:                                                         # simple clamping   0Pn = 20Pn�1 � 0Pn�2 and 0Pn+1 = 20Pn�1 � 0Pn�3.
                x.append(x[-1]*2-x[-2])                                         # 0P�1 = 20P0 � 0P1   and   0P�2 = 20P0 � 0P2. 
                x.append(x[-2]*2-x[-4])                                         # Note that the above grew the list already, so -2,-4 was really -1,-3 formerly.
                px1=x[0]*2-x[1]                                                 # 0Pn = 20Pn�1 � 0Pn�2   and   0Pn+1 = 20Pn�1 � 0Pn�3.
                px2=x[0]*2-x[2]                 
                x.insert(0,px1)
                x.insert(0,px2)                 
            elif link==2:                                               
                px1=(9-a)/4  * x[0] + (a-3)/2 * x[1] + (1-a)/4 * x[2]
                px2=(12-a)/2 * x[0] + (a-8)   * x[1] + (6-a)/2 * x[2]   
                x.insert(0,px1)
                x.insert(0,px2)                 
                px1=(9-a)/4  * x[-1] + (a-3)/2 * x[-2] + (1-a)/4 * x[-3] 
                px2=(12-a)/2 * x[-1] + (a-8)   * x[-2] + (6-a)/2 * x[-3]  
                x.append(px1)
                x.append(px2)                    
            elif link==4:                                                       # join without dropping points ?
                x.append(x[-1]*2-x[-2])                 
                px1=x[0]*2-x[1]                         
                x.insert(0,px1)
            j = 0                                
            tx=[]
            ptx=0
            while j < len(x):                   
                if j==len(x)-1 and link != 3:       
                    break
                if j == 0 and link != 3:                                        # Anchor start of output line to the start point
                    tx.append(x[j])
        
                elif j + 1 < len(x) or link==3:  
                    if link==3: 
                        ptx = ( a * x[( j - 1 )%(len(x)+1)] + ( 8 - 2 * a ) * x[j] + a * x[( j + 1 )%(len(x)+1)] ) / 8 
                    else: 
                        ptx = ( a * x[ j - 1 ] + ( 8 - 2 * a ) * x[j] + a * x[ j + 1 ] ) / 8       
                    tx.append(ptx)                  
                if link==3 or ( j + 2 < len(x) and j > 0 ):  
                    if link==3:  
                        ptx = ( ( b - 1 ) * x[(j -1)%(len(x)+1)] + ( 9 - b ) * x[ j ] + ( 9 - b ) * x[( j + 1 )%(len(x)+1)] + ( b - 1 ) * x[( j + 2 )%(len(x)+1)] ) / 16  
                    else: 
                        ptx = ( ( b - 1 ) * x[j -1] + ( 9 - b ) * x[ j ] + ( 9 - b ) * x[ j + 1 ] + ( b - 1 ) * x[ j + 2 ] ) / 16      
                    tx.append(ptx) 
                j=j+1 
            if link==3:  
                pass # skip push
            elif link>0:
                if k<sl:
                    tx=tx[3:-2]; # was -3
                else:
                    tx=tx[3:-1]; # put the actual end point back on the last one
            else: 
                tx.append(x[-1]) 
            x=tx.copy(); 
        if link==3:  
            x.append(x[0])                                                      #join end to start for drawing
        ret.append(x); 
    return ret


# cross-platform 'find our python'
# C:\Users\Administrator\AppData\Local\Autodesk\webdeploy\production\8b802e7a3c3d3db523b64fd80db49d9f63efcaf3\Python\Lib\venv\scripts\nt\pythonw.exe
def get_exec():
    try:
        #for ppath in (sys.exec_prefix, sys.executable, *sys.path, sys.argv[0]):
        for ppath in (sys.exec_prefix, sys.executable, *sys.path, sys.argv[0]):
            for subpath in (['bin'],['Python'],['']):
                for pyname in ('python.exe','python'): # pythonw prevents the unwanted black box popup - but fails to run due to env stuff
                    mypython=os.path.join(ppath,*subpath,pyname)
                    #eprint(mypython)
                    if os.path.isfile( mypython ): return mypython
    except: pass

    try:
        if sys.platform.startswith('darwin'):
            return os.path.join(sys.exec_prefix,'bin','python')
        else:
            return os.path.join(sys.path[0],'Python','python')

    except: return 'python' # give up searching - hope that the OS knows how to fix it itself...


# Do a web operation without making the user wait for it (threads). Fails in fusion (breaks their threads) if called via _thread.start_new_thread(web_req, ('u=u1.20200506&v=1.20200503&a=_aft&p=Airfoil_Tools',))
def web_req(req):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not s:
        return 0
    s.connect(("chrisdrake.com", 80))
    sent=s.send(b'GET /Airfoil_Tools/share.asp?'+str.encode(req)+b' HTTP/1.1\x0d\x0aHost: chrisdrake.com\x0d\x0aAccept-Encoding: identity\x0d\x0aUser-Agent: Python\x0d\x0aConnection: close\x0d\x0a\x0d\x0a') # was check_update.asp
    if sent==0:
        eprint("socket send problem")
        s.close()
        return 0

    chunk = s.recv(1024000)
    if chunk == b'':
        eprint("socket receive problem")
        s.close()
        return 0

    eprint('got {}.'.format(chunk))
    s.close()


# Do a web operation without making the user wait for it (nonblocking sockets). Call with parm to trigger.  call often with (None) to process
def web_nbreq(req):
    global pnl
    try: # suppress all errors - this gets run often from command handler
        if pnl.get('nbs',0) and pnl['nbs']: # already set up - do read/write when we get a chance
            eprint("-")
            ready_to_read, ready_to_write, in_error = select.select( [pnl['nbs']], [pnl['nbs']], [pnl['nbs']], 0.1)
            if len(in_error):
                eprint("e")
                eprint("non-blocking socket problem")
                pnl['nbs'].close()
                pnl['nbs']=None
                pnl['nbd']=None
            if len(ready_to_write) and pnl.get('nbd',''):
                eprint("s")
                sent=pnl['nbs'].send(pnl['nbd'])
                pnl['nbd']=None # clear - we've sent it now
            if len(ready_to_read):
                eprint("r")
                pnl['nbr'] = pnl['nbs'].recv(1024000)
                if pnl['nbr'] == b'':
                    eprint("socket receive problem")
                else:
                    eprint('got {}.'.format(pnl['nbr']))
                pnl['nbs'].close()
                pnl['nbs']=None
            return pnl['nbs']
        elif req: # initial call - set it up
            eprint("!")
            # stores socket 'nbs' and send data 'nbd' and response data 'nbr' in the global pnl[] structure
            pnl['nbs'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if not pnl['nbs']:
                return 0
            eprint("1")
            pnl['nbs'].setblocking(0)
            eprint("2")
            pnl['nbs'].connect_ex(("chrisdrake.com", 80))
            eprint("3")
            pnl['nbd']=b'GET /Airfoil_Tools/share.asp?'+str.encode(req)+b' HTTP/1.1\x0d\x0aHost: chrisdrake.com\x0d\x0aAccept-Encoding: identity\x0d\x0aUser-Agent: Python\x0d\x0aConnection: close\x0d\x0a\x0d\x0a' # was check_update.asp
            return web_nbreq(None) # try immediately
        # Future; how to do errors:
        #>>> err = sock.connect_ex(('10.0.0.1', 12345))
        #>>> import errno
        #>>> print errno.errorcode[err]
        #EINPROGRESS
        #>>> print sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        #61
        #>>> print errno.errorcode[61]
        #ECONNREFUSED
    except:
        eprint("web_nbreq problem")
        pass



# Get any updates that are awaiting - see also check_updates.py, the other half of this code.  Does not install updates (user gets asked first)
# Returns True if this is check_only and updates await.  Returns True if not check_only and all updates are applied
def updates(check_only):
    global updatedata
    latest_ver=updatedata
    uready=not check_only                                                       # starts with False for check_only, True for doing update (so doing-update returns "True" when done)
    ugotall=True
    nfiles=0

    #os.makedirs(home_folder, exist_ok=True)
    if latest_ver.get('updates',0):
        for updatefn in latest_ver['updates']:
            updfn=home_file(program_name, os.path.join('updates', updatefn))   # Put update files temporarily in the users data folder - the main program will apply the updates later if the user approves
            # check that the existing files, if any, are not corrupted, and remove if yes
            if os.path.isfile( updfn ):                     # Already fetched
                try:
                    if os.stat(updfn).st_size == latest_ver['updates'][updatefn]['len']:
                        uready=True
                        if check_only:
                            nfiles=nfiles+1
                            #vlog("{} Update file {} awaits".format(program_name,updfn))
                        else:
                            fn=os.path.join(prog_folder,updatefn)               # Work out where this needs to go
                            path=re.split("/|\\\\",fn)                          # Split path from filename, separator-agnostic
                            if path:
                                if len(path[0]) and path[0][-1]==':':
                                   path[0]=path[0]+os.sep                       # Python defaults to relative, but nothing else ever does...
                                fn=os.path.join(*path)                          # convert incoming / to outgoing \
                                path.pop()                                      # discard the file name 
                            vlog("{} Updating {} from {}".format(program_name,fn,updfn))
                            try:
                                if path: vlog('making path:{}.'.format(os.path.join(*path)))
                                if path: os.makedirs( os.path.join(*path), exist_ok=True)# Ensure path exists
                                with open( updfn, 'rb') as in_file:             # Open the temp file that was stored in the user home folder
                                    with open( fn, 'wb') as out_file:           # Prep to write to the target file
                                        out_file.write(in_file.read())          # Copy the file contents over
                                        out_file.close()
                                    in_file.close()
                                os.unlink(updfn)                                # Get rid of the updated file now
                            except:
                                vlog('{} Failed to update {} from {} - reason: {}'.format(program_name, fn, updfn, traceback.format_exc()))
                                ugotall=False                               # So caller knows we failed

                    else: # Wrong size - might still be downloading.  check_update.py takes care of removing corrupted files
                        uready=False
                        ugotall=False
                        vlog("{} Update file {} not fully downloaded yet".format(program_name,updfn))

                except:
                    vlog('{} update failed - please let us know about this problem: {}'.format(program_name, traceback.format_exc()))
            else: # not fetched, or, already done
                if check_only:
                    uready=False
                    ugotall=False
                    vlog("{} Update file {} not downloaded".format(program_name,updfn))

    if check_only and nfiles:
        vlog("{} of {} {} update file(s) await".format(nfiles,len(latest_ver['updates']),program_name))

    return uready and ugotall


#if __name__ == '__main__':
main_aft() # run this last, so everything is defined before use


'''

#########################
##### Design Plans ######
#########################

promo idea - world record for longest hand-thrown flight (cowl+wings)

store run history in preferences, including user metrics.

load/save into the project?
json_value = json.dumps(catch_me, sort_keys=True)
adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).attributes.add(self.group_name, 'settings', json_value)
json_value = json.loads( self._attributes_collection.itemByName(self.group_name, 'settings').value)



#    commandDefinitionPanel = ui.commandDefinitions.addButtonDefinition(aft+aftid, uiel[aftid]["name"], uiel[aftid]["desc"], resource_folder)
deleteMe
name
resourceFolder          Gets or sets the directory that contains any additional files associated with this command. These are typically the image files that will be used for a button and the html files for a tool clip or helps and tips.
toolClipFilename        Gets or sets the full filename of the image file (png) used for the tool clip. The tooltip is always shown but as the user hovers over the control it will progressively display the tool clip along with the tooltip text.
tooltip
commandCreated

controlDefinition       You can use properties on the control definition to define the look and behavior of the control.
#ida

CommandDefinitions Object
  addButtonDefinition
  addCheckBoxDefinition
  addListDefinition

StandardListType


#########################
##### FeatureCreep ######
#########################
min thickness
drawing outputs
polar perf outputs and charts
scan photo to airfoil
insert foil data into sketch (image PNGs of polar diagrams etc)
sqllite DB
RPM to V/Re
RE-Calculator can name and save results into settings file
username/password for web storage? (API to save in user account prolly better)

https://forums.autodesk.com/t5/fusion-360-api-and-scripts/add-in-announcement-hydrofoil-and-airfoil-tools-seeking-your/td-p/9453985


#########################
#####  Panel Plan  ######
#########################

About Airfoil Tools + help and videos

(solid): Create Wing or Strut
(solid): Create Cowling
(solid): Create Propellor or Turbine
(sketch): Insert " (same as above)

Import / Export airfoil data files
Airfoil data maintenance operations  [declutter] [normalize] [scale] [close] [spline/points-only] [compare] => can be sideways arrows in menus
Airfoil performance analysis
Airfoil CFD genetic optimiser
Reynolds (Re) Number Calcultor

Report Bug / Request Feature

File menu; import/export airfoil ?

Airfoil UX Design.
5 Tabs: Utilities, Wing/Strut, Cowling, Propellor/Turbine, Help/Support
Utilities: import DAT; [declutter] [normalize] [scale] [close] [spline/points-only]  (export?)
Quick-insert (medium;Air(alt+temp)/Water(sea/fresh/depth/temp)/other m2/s, chord, thick, speed (m,km,knots,mph,foot,etc) ,conditions(rough+turbulent, smoothe+laminar...)
Re computer
Performance Analysis
Optimize...
Compare. Investigate (most alike)
* Air
* Water
* [From KiV] - [To KiV] (filled by above, but selectable) - Kinematic Viscosity (http://airfoiltools.com/calculator/reynoldsnumber)  [Re info box?]
* Cord [nn] Thicknes[nn]
* Shape [Sketch name] ?ground plane? - see https://www.youtube.com/watch?v=qGQgMADxoFU
* Best Lift for Lowest Drag
* Lowest drag ( no lift )
* Highest lift ( poor drag )
Speed range [low]..[high] * m/s, km/h, knots, miles, etc...
Cruise [speed] [importance %]

prop/turbine - rpm, torque, hp/kw, amps/volts/phase efficiency, etc etc



#########################
#####  Handy Stuff ######
#########################


# Handy stuff for later:
returnValue = command_var.setDialogInitialSize(width, height)   # Set panel size

command_var.cancelButtonText = "No" # Change the word "Cancel" on the cancel button to something else

command_var.helpFile = resources+"/somefile.html" - adds (i) thing (left of OK at panel bottom) that opens browser to this supposedly

Good overview of interfacE: https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-F31C76F0-8C74-4343-904C-68FDA9BB8B4C

Emulate 3-point-rectangle process:
  pops up panel
  cursor says "select first corner"...

preSelect: - so we can allow users to select points or lines
https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-E3D24F04-8576-420E-B9AD-44746A6B12EE

Command.validateInputs 1Event

all 4 controls: command, drop-down, split-button, and separator.


Needs 4 x 3 = 12icons for every resource entry
    16x16.png - 16x16 pixel image showing the standard image.
    32x32.png - 32x32 pixel image showing the standard image.
    16x16@2x.png - This is a copy of the 32x32.png file that is used on a retina display for the equivalent of the 16x16 standard image.
    32x32@2x.png - 64x64 pixel image which is used on a retina display for the equivalent of the 32x32 standard image.

    All above, with -disabled : e.g. 32x32-disabled@2x.png  # for when not useable
    All above, with -dark : e.g. 32x32-disabled@2x.png      # for when actually being used - use dark blue background to appear depressed.

Preferences.defaultUnitsPreferences

When editing python in vim, use:-

:set tabstop=4
:set softtabstop=4
:set shiftwidth=4
:set expandtab

'''
