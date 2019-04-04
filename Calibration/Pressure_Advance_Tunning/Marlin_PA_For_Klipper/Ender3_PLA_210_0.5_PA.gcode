; ### Marlin K-Factor Calibration Pattern ###
; -------------------------------------------
;
; Created: Thu Apr 04 2019 13:05:30 GMT-0500 (Central Daylight Time)
;
; Settings Printer:
; Filament Diameter = 1.75 mm
; Nozzle Diameter = 0.6 mm
; Nozzle Temperature = 210 °C
; Bed Temperature = 60 °C
; Retraction Distance = 4 mm
; Layer Height = 0.5 mm
; Z-axis Offset = 0 mm
;
; Settings Print Bed:
; Bed Shape = Rect
; Bed Size X = 235 mm
; Bed Size Y = 235 mm
; Origin Bed Center = false
;
; Settings Speed:
; Slow Printing Speed = 1200 mm/min
; Fast Printing Speed = 3600 mm/min
; Movement Speed = 7200 mm/min
; Retract Speed = 1500 mm/min
; Printing Acceleration = 500 mm/s^2
; Jerk X-axis =  firmware default
; Jerk Y-axis =  firmware default
; Jerk Z-axis =  firmware default
; Jerk Extruder =  firmware default
;
; Settings Pattern:
; Linear Advance Version = 1.5
; Starting Value Factor = 0
; Ending Value Factor = 2
; Factor Stepping = 0.1
; Test Line Spacing = 5 mm
; Test Line Length Slow = 20 mm
; Test Line Length Fast = 40 mm
; Print Pattern = Standard
; Print Frame = false
; Number Lines = false
; Print Size X = 90 mm
; Print Size Y = 125 mm
; Print Rotation = 0 degree
;
; Settings Advance:
; Nozzle / Line Ratio = 1.2
; Bed leveling = 0
; Use FWRETRACT = false
; Extrusion Multiplier = 1
; Prime Nozzle = true
; Prime Extrusion Multiplier = 2.5
; Prime Speed = 1800
; Dwell Time = 2 s
;
; prepare printing
;
M104 S210 ; set nozzle temperature but do not wait
M190 S60 ; set bed temperature and wait
M109 S210 ; block waiting for nozzle temp
G28 ; home all axes with heated bed
G21 ; set units to millimeters
M204 P500 ; set acceleration
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
G92 E0 ; reset extruder distance
G1 X117.5 Y117.5 F7200 ; move to start
G1 Z0.5 F1200 ; move to layer height
;
; prime nozzle
;
G1 X72.5 Y55 F7200 ; move to start
G1 X72.5 Y180 E46.7721 F1800 ; print line
G1 X73.58 Y180 F7200 ; move to start
G1 X73.58 Y55 E46.7721 F1800 ; print line
G1 E-4 F1500 ; retract
;
; start the Test pattern
;
G4 P2000 ; Pause (dwell) for 2 seconds
G1 X82.5 Y55 F7200 ; move to start
M900 K0 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y55 E2.9934 F1200 ; print line
G1 X142.5 Y55 E5.9868 F3600 ; print line
G1 X162.5 Y55 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y60 F7200 ; move to start
M900 K0.1 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y60 E2.9934 F1200 ; print line
G1 X142.5 Y60 E5.9868 F3600 ; print line
G1 X162.5 Y60 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y65 F7200 ; move to start
M900 K0.2 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y65 E2.9934 F1200 ; print line
G1 X142.5 Y65 E5.9868 F3600 ; print line
G1 X162.5 Y65 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y70 F7200 ; move to start
M900 K0.3 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y70 E2.9934 F1200 ; print line
G1 X142.5 Y70 E5.9868 F3600 ; print line
G1 X162.5 Y70 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y75 F7200 ; move to start
M900 K0.4 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y75 E2.9934 F1200 ; print line
G1 X142.5 Y75 E5.9868 F3600 ; print line
G1 X162.5 Y75 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y80 F7200 ; move to start
M900 K0.5 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y80 E2.9934 F1200 ; print line
G1 X142.5 Y80 E5.9868 F3600 ; print line
G1 X162.5 Y80 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y85 F7200 ; move to start
M900 K0.6 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y85 E2.9934 F1200 ; print line
G1 X142.5 Y85 E5.9868 F3600 ; print line
G1 X162.5 Y85 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y90 F7200 ; move to start
M900 K0.7 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y90 E2.9934 F1200 ; print line
G1 X142.5 Y90 E5.9868 F3600 ; print line
G1 X162.5 Y90 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y95 F7200 ; move to start
M900 K0.8 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y95 E2.9934 F1200 ; print line
G1 X142.5 Y95 E5.9868 F3600 ; print line
G1 X162.5 Y95 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y100 F7200 ; move to start
M900 K0.9 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y100 E2.9934 F1200 ; print line
G1 X142.5 Y100 E5.9868 F3600 ; print line
G1 X162.5 Y100 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y105 F7200 ; move to start
M900 K1 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y105 E2.9934 F1200 ; print line
G1 X142.5 Y105 E5.9868 F3600 ; print line
G1 X162.5 Y105 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y110 F7200 ; move to start
M900 K1.1 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y110 E2.9934 F1200 ; print line
G1 X142.5 Y110 E5.9868 F3600 ; print line
G1 X162.5 Y110 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y115 F7200 ; move to start
M900 K1.2 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y115 E2.9934 F1200 ; print line
G1 X142.5 Y115 E5.9868 F3600 ; print line
G1 X162.5 Y115 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y120 F7200 ; move to start
M900 K1.3 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y120 E2.9934 F1200 ; print line
G1 X142.5 Y120 E5.9868 F3600 ; print line
G1 X162.5 Y120 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y125 F7200 ; move to start
M900 K1.4 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y125 E2.9934 F1200 ; print line
G1 X142.5 Y125 E5.9868 F3600 ; print line
G1 X162.5 Y125 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y130 F7200 ; move to start
M900 K1.5 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y130 E2.9934 F1200 ; print line
G1 X142.5 Y130 E5.9868 F3600 ; print line
G1 X162.5 Y130 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y135 F7200 ; move to start
M900 K1.6 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y135 E2.9934 F1200 ; print line
G1 X142.5 Y135 E5.9868 F3600 ; print line
G1 X162.5 Y135 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y140 F7200 ; move to start
M900 K1.7 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y140 E2.9934 F1200 ; print line
G1 X142.5 Y140 E5.9868 F3600 ; print line
G1 X162.5 Y140 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y145 F7200 ; move to start
M900 K1.8 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y145 E2.9934 F1200 ; print line
G1 X142.5 Y145 E5.9868 F3600 ; print line
G1 X162.5 Y145 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y150 F7200 ; move to start
M900 K1.9 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X102.5 Y150 E2.9934 F1200 ; print line
G1 X142.5 Y150 E5.9868 F3600 ; print line
G1 X162.5 Y150 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X82.5 Y155 F7200 ; move to start
;
; mark the test area for reference
;
M900 K0 ; set K-factor 0
G1 X102.5 Y160 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X102.5 Y180 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X142.5 Y160 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X142.5 Y180 E2.9934 F1200 ; print line
G1 E-4 F1500 ; retract
G1 Z0.6 F1200 ; zHop
;
; finish
;
M104 S0 ; turn off hotend
M140 S0 ; turn off bed
G1 Z30 X235 Y235 F7200 ; move away from the print
M84 ; disable motors
M502 ; resets parameters from ROM
M501 ; resets parameters from EEPROM
;