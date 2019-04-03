; ### Marlin K-Factor Calibration Pattern ###
; -------------------------------------------
;
; Created: Wed Apr 03 2019 14:16:07 GMT-0500 (Central Daylight Time)
;
; Settings Printer:
; Filament Diameter = 1.75 mm
; Nozzle Diameter = 0.5 mm
; Nozzle Temperature = 215 °C
; Bed Temperature = 60 °C
; Retraction Distance = 4 mm
; Layer Height = 0.4 mm
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
; Factor Stepping = 0.2
; Test Line Spacing = 5 mm
; Test Line Length Slow = 20 mm
; Test Line Length Fast = 40 mm
; Print Pattern = Standard
; Print Frame = false
; Number Lines = true
; Print Size X = 98 mm
; Print Size Y = 75 mm
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
M104 S215 ; set nozzle temperature but do not wait
M190 S60 ; set bed temperature and wait
M109 S215 ; block waiting for nozzle temp
G28 ; home all axes with heated bed
G21 ; set units to millimeters
M204 P500 ; set acceleration
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
G92 E0 ; reset extruder distance
G1 X117.5 Y117.5 F7200 ; move to start
G1 Z0.4 F1200 ; move to layer height
;
; prime nozzle
;
G1 X68.5 Y80 F7200 ; move to start
G1 X68.5 Y155 E18.7088 F1800 ; print line
G1 X69.4 Y155 F7200 ; move to start
G1 X69.4 Y80 E18.7088 F1800 ; print line
G1 E-4 F1500 ; retract
;
; start the Test pattern
;
G4 P2000 ; Pause (dwell) for 2 seconds
G1 X78.5 Y80 F7200 ; move to start
M900 K0 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y80 E1.9956 F1200 ; print line
G1 X138.5 Y80 E3.9912 F3600 ; print line
G1 X158.5 Y80 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y85 F7200 ; move to start
M900 K0.2 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y85 E1.9956 F1200 ; print line
G1 X138.5 Y85 E3.9912 F3600 ; print line
G1 X158.5 Y85 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y90 F7200 ; move to start
M900 K0.4 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y90 E1.9956 F1200 ; print line
G1 X138.5 Y90 E3.9912 F3600 ; print line
G1 X158.5 Y90 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y95 F7200 ; move to start
M900 K0.6 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y95 E1.9956 F1200 ; print line
G1 X138.5 Y95 E3.9912 F3600 ; print line
G1 X158.5 Y95 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y100 F7200 ; move to start
M900 K0.8 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y100 E1.9956 F1200 ; print line
G1 X138.5 Y100 E3.9912 F3600 ; print line
G1 X158.5 Y100 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y105 F7200 ; move to start
M900 K1 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y105 E1.9956 F1200 ; print line
G1 X138.5 Y105 E3.9912 F3600 ; print line
G1 X158.5 Y105 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y110 F7200 ; move to start
M900 K1.2 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y110 E1.9956 F1200 ; print line
G1 X138.5 Y110 E3.9912 F3600 ; print line
G1 X158.5 Y110 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y115 F7200 ; move to start
M900 K1.4 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y115 E1.9956 F1200 ; print line
G1 X138.5 Y115 E3.9912 F3600 ; print line
G1 X158.5 Y115 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y120 F7200 ; move to start
M900 K1.6 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y120 E1.9956 F1200 ; print line
G1 X138.5 Y120 E3.9912 F3600 ; print line
G1 X158.5 Y120 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y125 F7200 ; move to start
M900 K1.8 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y125 E1.9956 F1200 ; print line
G1 X138.5 Y125 E3.9912 F3600 ; print line
G1 X158.5 Y125 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y130 F7200 ; move to start
M900 K2 ; set K-factor
G1 E4 F1500 ; un-retract
G1 X98.5 Y130 E1.9956 F1200 ; print line
G1 X138.5 Y130 E3.9912 F3600 ; print line
G1 X158.5 Y130 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X78.5 Y135 F7200 ; move to start
;
; mark the test area for reference
;
M900 K0 ; set K-factor 0
G1 X98.5 Y135 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X98.5 Y155 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 X138.5 Y135 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X138.5 Y155 E1.9956 F1200 ; print line
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
;
; print K-values
;
G1 X160.5 Y78 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X162.5 Y78 E0.1996 F1200 ; 0
G1 X162.5 Y80 E0.1996 F1200 ; 0
G1 X162.5 Y82 E0.1996 F1200 ; 0
G1 X160.5 Y82 E0.1996 F1200 ; 0
G1 X160.5 Y80 E0.1996 F1200 ; 0
G1 X160.5 Y78 E0.1996 F1200 ; 0
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
G1 X160.5 Y88 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X162.5 Y88 E0.1996 F1200 ; 0
G1 X162.5 Y90 E0.1996 F1200 ; 0
G1 X162.5 Y92 E0.1996 F1200 ; 0
G1 X160.5 Y92 E0.1996 F1200 ; 0
G1 X160.5 Y90 E0.1996 F1200 ; 0
G1 X160.5 Y88 E0.1996 F1200 ; 0
G1 E-4 F1500 ; retract
G1 X163.5 Y88 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X163.5 Y88.4 E0.0399 F1200 ; dot
G1 E-4 F1500 ; retract
G1 X164.5 Y88 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X164.5 Y90 F7200 ; move to start
G1 X164.5 Y92 F7200 ; move to start
G1 X164.5 Y90 E0.1996 F1200 ; 4
G1 X166.5 Y90 E0.1996 F1200 ; 4
G1 X166.5 Y92 F7200 ; move to start
G1 X166.5 Y90 E0.1996 F1200 ; 4
G1 X166.5 Y88 E0.1996 F1200 ; 4
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
G1 X160.5 Y98 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X162.5 Y98 E0.1996 F1200 ; 0
G1 X162.5 Y100 E0.1996 F1200 ; 0
G1 X162.5 Y102 E0.1996 F1200 ; 0
G1 X160.5 Y102 E0.1996 F1200 ; 0
G1 X160.5 Y100 E0.1996 F1200 ; 0
G1 X160.5 Y98 E0.1996 F1200 ; 0
G1 E-4 F1500 ; retract
G1 X163.5 Y98 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X163.5 Y98.4 E0.0399 F1200 ; dot
G1 E-4 F1500 ; retract
G1 X164.5 Y98 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X164.5 Y100 F7200 ; move to start
G1 X166.5 Y100 E0.1996 F1200 ; 8
G1 X166.5 Y98 E0.1996 F1200 ; 8
G1 X164.5 Y98 E0.1996 F1200 ; 8
G1 X164.5 Y100 E0.1996 F1200 ; 8
G1 X164.5 Y102 E0.1996 F1200 ; 8
G1 X166.5 Y102 E0.1996 F1200 ; 8
G1 X166.5 Y100 E0.1996 F1200 ; 8
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
G1 X160.5 Y108 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X160.5 Y110 E0.1996 F1200 ; 1
G1 X160.5 Y112 E0.1996 F1200 ; 1
G1 E-4 F1500 ; retract
G1 X161.5 Y108 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X161.5 Y108.4 E0.0399 F1200 ; dot
G1 E-4 F1500 ; retract
G1 X162.5 Y108 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X162.5 Y110 F7200 ; move to start
G1 X162.5 Y112 F7200 ; move to start
G1 X164.5 Y112 E0.1996 F1200 ; 2
G1 X164.5 Y110 E0.1996 F1200 ; 2
G1 X162.5 Y110 E0.1996 F1200 ; 2
G1 X162.5 Y108 E0.1996 F1200 ; 2
G1 X164.5 Y108 E0.1996 F1200 ; 2
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
G1 X160.5 Y118 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X160.5 Y120 E0.1996 F1200 ; 1
G1 X160.5 Y122 E0.1996 F1200 ; 1
G1 E-4 F1500 ; retract
G1 X161.5 Y118 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X161.5 Y118.4 E0.0399 F1200 ; dot
G1 E-4 F1500 ; retract
G1 X162.5 Y118 F7200 ; move to start
G1 E4 F1500 ; un-retract
G1 X162.5 Y120 F7200 ; move to start
G1 X164.5 Y120 E0.1996 F1200 ; 6
G1 X164.5 Y118 E0.1996 F1200 ; 6
G1 X162.5 Y118 E0.1996 F1200 ; 6
G1 X162.5 Y120 E0.1996 F1200 ; 6
G1 X162.5 Y122 E0.1996 F1200 ; 6
G1 X164.5 Y122 E0.1996 F1200 ; 6
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
G1 X160.5 Y128 F7200 ; move to start
G1 Z0.4 F1200 ; zHop
G1 E4 F1500 ; un-retract
G1 X160.5 Y130 F7200 ; move to start
G1 X160.5 Y132 F7200 ; move to start
G1 X162.5 Y132 E0.1996 F1200 ; 2
G1 X162.5 Y130 E0.1996 F1200 ; 2
G1 X160.5 Y130 E0.1996 F1200 ; 2
G1 X160.5 Y128 E0.1996 F1200 ; 2
G1 X162.5 Y128 E0.1996 F1200 ; 2
G1 E-4 F1500 ; retract
G1 Z0.5 F1200 ; zHop
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