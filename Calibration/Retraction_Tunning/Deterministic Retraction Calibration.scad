/*
Deterministic Retraction Calibration
Written by David Orgeman - 2015
Released under the Creative Commons Attribution-ShareAlike license
CC BY-SA

This creates a calibration object with a vertical fin that has a gap
of a specified size.  The object is designed so that most slicers will
cause retract to occur on one side of the gap, the printhead to then
travel directly to the other side of the gap, and reload to then occur.
This allows careful examination and tuning of the retraction parameters
to improve print quality.  Because the object is easy to print and does
not depend on other challenging capabilities, this allows tuning even
on a printer that is still a long ways from printing cleanly.  It is
adjustable if the default parameters do not work for some specific
printer.  The base of the object has on indent indicating the side of
the gap where retract took place, and a bump indicating the side where
reload happened.  Those markers can be flipped if the slicer in use
causes a different path from what I have generally seen.
*/



//PARAMETERS

//gap over which the retract will travel
WallGap=40;

//single extrusion width wall thickness
WallWidth=0.65;

//height of the calibration object
WallHeight=6;

//length of the wall on each side of the gap
WallLength=15;

//width of the calibration object
BaseWidth=8;

//print retract and reload normal(1) or inverted(-1)
Flipper=1;//[1,-1]



Retraction();



module Retraction() {
	difference() {
		union() {
			translate([0,-BaseWidth/2,0])
				cube([2*WallLength+WallGap,BaseWidth,1]);
			translate([0,-WallWidth/2,0])
				cube([WallLength,WallWidth,WallHeight]);
			translate([WallLength+WallGap,-WallWidth/2,0])	
				cube([WallLength,WallWidth,WallHeight]);
			translate([WallLength+WallGap/2-Flipper*0.4*BaseWidth/2,BaseWidth/2,0])
				cylinder(r=0.4*BaseWidth/2,h=1,$fn=32);
			translate([WallLength+WallGap/2-Flipper*0.4*BaseWidth/2,-BaseWidth/2,0])
				cylinder(r=0.4*BaseWidth/2,h=1,$fn=32);
		}
			translate([WallLength+WallGap/2+Flipper*0.4*BaseWidth/2,BaseWidth/2,-1])
				cylinder(r=0.4*BaseWidth/2,h=3,$fn=32);
			translate([WallLength+WallGap/2+Flipper*0.4*BaseWidth/2,-BaseWidth/2,-1])
				cylinder(r=0.4*BaseWidth/2,h=3,$fn=32);
	}
}