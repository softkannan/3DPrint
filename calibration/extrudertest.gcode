G90 ; Absolute positioning
M104 S210
G28 Z; Home Z axis
G0 F240 Z50 ; Raise Z
G28 X Y; Home X and Y axis
G0 F3000 X0 Y0 ; Go to printer home
M109 S210
G92 E0
; Extruder Benchmark at 15 mm^3/s
G1 F374 E100
G0 F3000 X5