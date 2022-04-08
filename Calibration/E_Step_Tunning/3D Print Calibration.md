## 3D Print Calibration

### Extruder Steps Calibration

First Measure out 120mm and mark the filament from known measuring point from extruder (before it enters the extruder).

Move Extruder 100mm at 100mm/min speed using following G-Code `G1 E100 F100`

After Extruder Stops Measure Out the remaining filament length.

I measured out 25mm remaining which means i have under extruded about 5mm.

New E Steps = Desired Distance / Measured Distance * Current E Steps

98 = 100 / 95 * 93

Enter this value to your config file.

Current Value is 100 Steps

### Extrusion Multiplier / Flow Rate

Use calibration cude and print no infill, no top / bottom and only one line with wall.

Just print up to the point we can measure

New Extrusion Multiplier = Desired Wall Thickness / Measured Wall Thickness * Existing Extrusion Multiplier

Desired Wall Thickness
-	On Simplify 3D is is Auto Calculated, normally for .4mm nozzle size it is 0.48mm
-	On Cura it marked as 0.5 mm for 0.4mm nozzle size
-	On Slic3r it 0.5 mm for 0.4 mm nozzle size

91	= 0.4 / 0.44 * 100

Current Value for PLA 93
Current Value for PETG 
