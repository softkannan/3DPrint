; Ender 3 Custom Start G-code
; begin heating bed
M140 S[first_layer_bed_temperature]
G28 ; Home all axes
; begin heating nozzle
M104 S[first_layer_temperature]
; Wait for bed temp
M190 S[first_layer_bed_temperature]
; Wait for nozzle temp
M109 S[first_layer_temperature]
G21 ; set units to millimeters
G90 ; use absolute coordinates
G92 E0 ; Reset Extruder
G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position
G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line
G1 X0.4 Y200.0 Z0.3 F5000.0 ; Move to side a little
G1 X0.4 Y20 Z0.3 F1500.0 E30 ; Draw the second line
G1 E-4.00000 F1500.00000 ; retract
G1 X50 Y20 Z0.3 F1500.0 ; Slight side move
G92 E0 ; Reset Extruder
G1 X100 Y20 Z0.4 F1500.0 ; Slight side move
; End of custom start GCode