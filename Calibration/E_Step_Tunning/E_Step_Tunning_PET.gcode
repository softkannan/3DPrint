; begin heating nozzle
M104 S235
G28 ; Home all axes
G21 ; set units to millimeters
G90 ; use absolute coordinates
M82 ; use absolute distances for extrusion
; Wait for nozzle temp
M109 S235
G92 X0 Y0 Z0 E0 ; Set cords to zero
G1 E100 F100 ; move extruder 1 100mm 
M84 ; disable steppers