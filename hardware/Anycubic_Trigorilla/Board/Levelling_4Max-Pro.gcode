; Assisted Bed Levelling
; for Anycubic 4Max Pro
; by alfrank

; performs 5 cycles of 
; going to each corner and the center
; waiting at each point for 15 seconds
; to allow manual bed height adjustments
; by using the four thumbscrews

; CAUTION - BED & NOZZLE ARE HOT !!!

G21 ; set units to millimeters
G90 ; absolute positioning
M107 ; turn all fans off
M140 S60 ; set bed temperature
M104 S230 ; set hotend temperature
G28 X Y ; home X and Y axis
G28 Z ; home Z axis
M190 S60 ; wait for bed temperature
M109 S230 ; wait for hotend temperature


; Cycle 1 of 5

;Go to Position 1 - Front Left Corner
G1 Z10 F500
G1 X30 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 2 - Front Right Corner
G1 Z10 F500
G1 X240 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 3 - Rear Right Corner
G1 Z10 F500
G1 X240 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 4 - Rear Left Corner
G1 Z10 F500
G1 X30 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 5 - Center
G1 Z10 F500
G1 X135 Y105 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds


; Cycle 2 of 5

;Go to Position 1 - Front Left Corner
G1 Z10 F500
G1 X30 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 2 - Front Right Corner
G1 Z10 F500
G1 X240 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 3 - Rear Right Corner
G1 Z10 F500
G1 X240 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 4 - Rear Left Corner
G1 Z10 F500
G1 X30 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 5 - Center
G1 Z10 F500
G1 X135 Y105 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds


; Cycle 3 of 5

;Go to Position 1 - Front Left Corner
G1 Z10 F500
G1 X30 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 2 - Front Right Corner
G1 Z10 F500
G1 X240 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 3 - Rear Right Corner
G1 Z10 F500
G1 X240 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 4 - Rear Left Corner
G1 Z10 F500
G1 X30 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 5 - Center
G1 Z10 F500
G1 X135 Y105 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds


; Cycle 4 of 5

;Go to Position 1 - Front Left Corner
G1 Z10 F500
G1 X30 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 2 - Front Right Corner
G1 Z10 F500
G1 X240 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 3 - Rear Right Corner
G1 Z10 F500
G1 X240 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 4 - Rear Left Corner
G1 Z10 F500
G1 X30 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 5 - Center
G1 Z10 F500
G1 X135 Y105 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds


; Cycle 5 of 5

;Go to Position 1 - Front Left Corner
G1 Z10 F500
G1 X30 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 2 - Front Right Corner
G1 Z10 F500
G1 X240 Y30 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 3 - Rear Right Corner
G1 Z10 F500
G1 X240 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 4 - Rear Left Corner
G1 Z10 F500
G1 X30 Y175 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to Position 5 - Center
G1 Z10 F500
G1 X135 Y105 F3600
G1 Z0 F500
M300 S880 P750 ;  beep at 880 Hz (A5) for 0.75 seconds
G4 S15 ; pause 15 seconds

;Go to front left
G1 Z10 F500
G1 X10 Y10 F3600

G28
M104 S0 ; turn off nozzle
M140 S0 ; turn off bed
M82 ; disable motors