; Ender 3 Custom End G-code
G4 ; Wait
M220 S100 ; Reset Speed factor override percentage to default (100%)
M221 S100 ; Reset Extrude factor override percentage to default (100%)
G91 ; Set coordinates to relative
G1 F1500 E-3 ; Retract filament 3 mm to prevent oozing
G1 F3000 Z20 ; Move Z Axis up 20 mm to allow filament ooze freely
G1 F1500 E-75 ; Retract all filament
G1 F1500 E-75 ; Retract all filament
G1 F1500 E-75 ; Retract all filament
G1 F1500 E-75 ; Retract all filament
G1 F1500 E-75 ; Retract all filament
G90 ; Set coordinates to absolute
G1 X0 Y235 F1800 ; Move Heat Bed to the front for easy print removal
G1 F3000 Z100 ; Move Z Axis up 100 mm to allow filament ooze freely
M140 S0 ; turn off heated bed
M106 S255 ; set fan to 100
M109 R35 ; cool down hot end to 35
M106 S0 ; set fan to 0
M84 ; Disable stepper motors
; End of custom end GCode