M201 X500 Y500 Z100 E5000 ; sets maximum accelerations, mm/sec^2
M203 X500 Y500 Z5 E25 ; sets maximum feedrates, mm/sec
M204 S500 T500 ; sets acceleration (S) and retract acceleration (T)
M205 X10 Y10 Z0.3 E5.0 ; sets the jerk limits, mm/sec
M205 S0 T0 ; sets the minimum extruding and travel feed rate, mm/sec

M117 Heating... ;Put printing message on LCD screen
M300 S2500 P100; Beep
;M221 S{if layer_height<0.075}100{else}95{endif} ; Set flow
M104 S[first_layer_temperature] ; set extruder temp
M140 S[first_layer_bed_temperature] ; set bed temp
G1 Z20 ; this is a good start heating position
G28 X Y; Home XY
M84 ; disable motors
M190 S[first_layer_bed_temperature] ; wait for bed temp
M109 S[first_layer_temperature] ; wait for extruder temp

; Start of print
G21; metric values
G90 ; absolute positioning
M82; set extruder to absolute mode

G28;

; Prepare nozzle
G92 E0 ; Set extrusion distance to 0
G92 E0 ; Set extrusion distance to 0
G1 F1800 E3;
G92 E0 ; Set extrusion distance to 0
G90;


; You may want to adjust the X and Y here so the nozzle is really above the bed!
G1 X5.0 Y5.0 F7200 ; Move to a position in the left front of the bed
G1 Z0.6; Move nozzle above 0.6 mm of the bed

G91 ; Use relative mode
; Make some jerky zick-zack move at the beginning
; This is supposed to get rid of residue at the nozzle
G1 X1.0 Y5.0 Z-0.1 E-1.0 F7200 ; X6 Y10 Z0.1, retract a tiny bit / 120mm/s
G1 X1.0 Y-5.0 Z0.1 E2.0 F7200 ; X7 Y5 Z0.2 extrude a tiny bit
G1 X2.0 Y5.0 Z-0.1 F7200 ; X9 Y10 Z0.1
G1 X2.0 Y-5.0 Z0.1 F7200 ; X11 Y5 Z0.2
G1 X2.0 Y5.0 F7200 ; X13 Y10
G1 X2.0 Y-5.0 F7200 ; X15 Y5

; now print a line of filament to prepare extrusion
G1 Y50 E20 F1000 ; prints a line in the front
G1 Y50 E40 F1000 ; prints a line in the front

; Done with the dancing :)
G92 E0 ; Set extrusion distance to 0
G90 ; switch back to absolute mode

M117 Printing... ;Put printing message on LCD screen
; Start of actual GCode for the print