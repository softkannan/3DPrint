G1 F3600 ; set standard speed
G28 X ; position X for easy part removal
G90 ; absolute positioning
G1 Y205 ; position Y for easy part removal
G91 ; relative positioning
G1 Z50 ; position Z for easy part removal
M300 S0 P250 ; pause for 0.25 seconds 
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
M300 S0 P250 ; pause for 0.25 seconds 
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
M300 S0 P250 ; pause for 0.25 seconds 
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
M300 S0 P250 ; pause for 0.25 seconds 
M106 S0 ; fan off
M104 S200 ; reduce extruder heat
M140 S60 ; reduce bed heat
M84 ; disable motors
