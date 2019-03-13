;K Line Test created by Sebastianv650

M107
M83  ; extruder relative mode
M104 S215 ; set extruder temp
M140 S60 ; set bed temp
M190 S60 ; wait for bed temp
M109 S215 ; wait for extruder temp
G28 ; home all without mesh bed level
G1 Y-3.0 F1000.0 ; go outside print area
G1 X60.0 E9.0  F1000.0 ; intro line
G1 X100.0 E12.5  F1000.0 ; intro line
G21 ; set units to millimeters
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
G1 Z0.200 F7200.000
M204 S500
;20mm/s = F1200
;70mm/s = F4200
;120mm/s = F7200
G1 E-0.80000 F2100.00000
G1 X10 Y10 F7200.000
G1 E0.80000 F2100.00000
M900 K0
G1 X10 Y20 E0.37418 F1200 ;Prime, travel to first testline
G1 X30 Y20 E0.74835 F1200 ;Slow part
G1 X60 Y20 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X80 Y20 E0.74835 F1200 ;Slow part
M900 K10
G1 X80 Y30 E0.37418 F1200 ;Travel to next testline
G1 X60 Y30 E0.74835 F1200 ;Slow part
G1 X30 Y30 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X10 Y30 E0.74835 F1200 ;Slow part
M900 K20
G1 X10 Y40 E0.37418 F1200 ;Travel to next testline
G1 X30 Y40 E0.74835 F1200 ;Slow part
G1 X60 Y40 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X80 Y40 E0.74835 F1200 ;Slow part
M900 K30
G1 X80 Y50 E0.37418 F1200 ;Travel to next testline
G1 X60 Y50 E0.74835 F1200 ;Slow part
G1 X30 Y50 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X10 Y50 E0.74835 F1200 ;Slow part
M900 K40
G1 X10 Y60 E0.37418 F1200 ;Travel to next testline
G1 X30 Y60 E0.74835 F1200 ;Slow part
G1 X60 Y60 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X80 Y60 E0.74835 F1200 ;Slow part
M900 K50
G1 X80 Y70 E0.37418 F1200 ;Travel to next testline
G1 X60 Y70 E0.74835 F1200 ;Slow part
G1 X30 Y70 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X10 Y70 E0.74835 F1200 ;Slow part
M900 K60
G1 X10 Y80 E0.37418 F1200 ;Travel to next testline
G1 X30 Y80 E0.74835 F1200 ;Slow part
G1 X60 Y80 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X80 Y80 E0.74835 F1200 ;Slow part
M900 K70
G1 X80 Y90 E0.37418 F1200 ;Travel to next testline
G1 X60 Y90 E0.74835 F1200 ;Slow part
G1 X30 Y90 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X10 Y90 E0.74835 F1200 ;Slow part
M900 K80
G1 X10 Y100 E0.37418 F1200 ;Travel to next testline
G1 X30 Y100 E0.74835 F1200 ;Slow part
G1 X60 Y100 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X80 Y100 E0.74835 F1200 ;Slow part
M900 K90
G1 X80 Y110 E0.37418 F1200 ;Travel to next testline
G1 X60 Y110 E0.74835 F1200 ;Slow part
G1 X30 Y110 E1.12253 F4200 ;Accelerate - cruise - decelerate
G1 X10 Y110 E0.74835 F1200 ;Slow part
G1 E-0.80000 F2100.00000
M107
G4 ; wait
M104 S0 ; turn off temperature
M140 S0 ; turn off heatbed
M107 ; turn off fan
G91; relative cooridantes
G1 Z1 F4500;
G90; set absolute coordinates
G1 X0 Y200; home X axis
M84 ; disable motors