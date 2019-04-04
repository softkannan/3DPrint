G28 ; Home all axes
G1 Z5.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 Z10 ; Lift Z axis
G1 X32 Y35 ; Move to Position 1
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X32 Y206 ; Move to Position 2
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X202 Y206 ; Move to Position 3
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X202 Y35 ; Move to Position 4
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X32 Y35 ; Move to Position 1
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X32 Y206 ; Move to Position 2
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X202 Y206 ; Move to Position 3
G1 Z0
M0 ; Pause print
G1 Z10 ; Lift Z axis
G1 X202 Y35 ; Move to Position 4
G1 Z0
M0 ; Pause print
M220 S100 ; Reset Speed factor override percentage to default (100%)
M221 S100 ; Reset Extrude factor override percentage to default (100%)
G1 Z20 ; Move Z Axis up 10 mm to allow filament ooze freely
M106 S0 ; Turn off Cooling Fan
M107 ; Turn off Fan
M84 ; Disable stepper motors
