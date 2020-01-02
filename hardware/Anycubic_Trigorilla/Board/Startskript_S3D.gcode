G21 ; set units to millimeters
G90 ; absolute positioning
G1 F3600 ; set standard speed
M107 ; turn all fans off
M140 S[bed0_temperature] ; set bed temperature
M104 S[extruder0_temperature] ; set hotend temperature
G28 X Y ; home X and Y axis
G28 Z ; home Z axis
M190 S[bed0_temperature] ; wait for bed temperature
M109 S[extruder0_temperature] ; wait for hotend temperature
G92 E0.0 ; reset extruder distance position
G1 Y40.0 ; wipe nozzle on brass brush
G1 Y5.0 ; wipe nozzle on brass brush
G1 Y40.0 ; wipe nozzle on brass brush
G1 Y5.0 ; wipe nozzle on brass brush
G1 X0.0 Z0.25 ; set starting point
G1 Y60.0 E4.5 F1000.0 ; print intro line
G1 Y100.0 E21.5 F1000.0 ; print intro line
G92 E0.0 ; reset extruder distance position
