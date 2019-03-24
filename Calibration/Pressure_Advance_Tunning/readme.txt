
FW with Pressure Advance of 0.88 and PA Lookup Time of 0.1, Combing Mode: noskin, Retraction Speed: 65mm/sec, Retraction Distance: 6mm, Initial Layer Horizontal Expansion: -0.2mm, Outer Walls Before Inner Walls: True, Print Speed: 100mm/sec, Infill Density: 10%, In Klipper's Printer.cfg file, I added two lines:, pressure_advance: 0.88, pressure_advance_lookahead_time: 0.1, If I'm printing a model that needs supports, I usually switch the support pattern to Cross, and the Z-distance to 0.2mm (default is zigzag and 0.1mm, which I find harder to remove). I do not print miniatures, so depending on what you're printing, you may or may not find these settings useful. If I'm printing in vase mode (Spiralize Outer Contour in Cura), I will often bump the flow setting up to ensure that I get a solid, slightly thicker than default wall. This is helpful if you want a water-tight vase. Also may want to increase the number of bottom layers if you want water-tight.

My current solution is using a very low max_accel_to_decel (500), and a faster square_corner_velocity (10). This allows me to run higher PA values and get reasonable results with bowden. My last few prints were good enough that I've considered staying with bowden, but at some point I'll probably switch to a direct extruder to avoid these issues.

used the default config file titled "Ender 3 2018" that Klipper provides. Only thing changed was the max accel rate from 3000 to 1500. Then I added pressure advance @ 0.50, look ahead rate @ 0.075, and square corner velocity @ 5.0 (default).

0.24 layers @ 60mm/s, 800mm/s accel and 15mm/s square corner velocity, PA 0.450 with 0.01 look ahead, 2.5mm retraction @ 25mm/s with 0.064 extra prime

With capricorn tubing pressure advance 0.400 set retraction to 2-4mm at 25mm/s, max accel :500

retraction distance : 2.0mm, retraction speed : 45mm/s, pressure advance : 0.0100, pressure advance lookahead : 0.010
