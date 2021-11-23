;Example code courtesy of DIY3DTech.com
G21 ;metric values
G90 ;absolute positioning
M82 ;set extruder to absolute mode
M107 ;set fan off
G28 X0 Y0 ;move X/Y to min endstops
G28 Z0 ;move Z to min endstops
G1 Z30.0 F9000 ;move platform to clear indicator
G92 E0 ;zero the extruded length
G92 E0 ;zero the extruded length again
G1 F9000
M107 ;set fan off

;--------------Main Code-------------------------------------------------
G0 F3500 X30.000 Y65.00 Z10.000 ;move nozzle away from home point
G0 Z150.00 ;move z to 150mm (adjust as needed)
G0 Z10.00 ;move z back down (adjust as needed)
G0 Z150.00 ;move z to 150mm (adjust as needed)
;finnish and return to home postion (you can add more G0 loops if you need)
G28 X0 Y0 ;move X/Y to min endstops
G28 Z0 ;move Z to min endstops

;--------------Footer Code-----------------------------------------------------
M107
G0 F9000 X30 Y40 Z50
;End GCode
M104 S0 ;extruder heater off
M140 S0 ;heated bed heater off (if you have it)
G91 ;relative positioning
M84 ;steppers off
G90 ;absolute positioning