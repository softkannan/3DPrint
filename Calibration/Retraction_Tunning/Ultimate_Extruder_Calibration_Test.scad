// ***********
// * SUMMARY *
// ***********

//Flow rate and feed rate are no longer difficult to calibrate, thanks to stepper extruders. However, to really get your print quality to the next level, you will need to calibrate temperature and reversal settings for a given material. (and/or travel feed rate, depending on your machine) This is a fully parametric calibration test for both bridging and gap distances within the same part.

//Bridging is a great test for temperature. If the bridge is too saggy, the temperature is too high. There are also some advantages to higher temperatures though, one of which is it makes the thermoplastic less viscous, creating less work for the motor. If your preference is printing really hot, a fan concentrating cool air on the extrudate can also be used to calibrate bridging.

//Traversing large gaps is obviously a great test for reversal/travel speed settings. Set extra shells to 0 to avoid hiding any ooze behind inner perimeters. Make the infill very low to save printing time since you only care about spanning gaps for this test. Use a camera for feedback if you are extra picky about strings.

// ****************
// * INSTRUCTIONS *
// ****************

//To customize your test, open the script with OpenSCAD, and edit the variables labeled at the top. Once you are finished, select "Compile and Render" or press F6.

//PRIMARY INPUTS
//minimum reversal gap distance (mm)
//maximum reversal gap distance (mm)
//minimum bridging distance (mm)
//maximum bridging distance (mm)
//number of steps
//total height of object (mm)

//SECONDARY INPUTS
//width of vertical tower (mm)
//width of border on base plane (mm)
//thickness of border on base plane (mm)
//thickness of bridges (mm)

//PRIMARY INPUTS
gdmin = 20;     //minimum reversal gap distance (mm)
gdmax = 50;	//maximum reversal gap distance (mm)	
bdmin = 10;	//minimum bridging distance (mm)
bdmax = 60;	//maximum bridging distance (mm)
increment = 10;    //number of steps
height = 50;     //total height of object (mm)

//SECONDARY INPUTS
towerwidth = 3;     //width of vertical tower (mm)
borderwidth = 6;     //width of border on base plane (mm)
borderthickness = 0.5;     //thickness of border on base plane (mm)
bridgethickness = 2;     //thickness of bridges (mm)

//Script
xstepsize = (gdmax-gdmin)/increment; 
ystepsize = (bdmax-bdmin)/(increment);
zstepsize = height/increment;

union(){

difference(){
translate([-towerwidth,0,0]) cube([gdmin+xstepsize*(increment+1),ystepsize*(increment+2),borderthickness]);

translate([-towerwidth+borderwidth,borderwidth,0]) cube([gdmin+xstepsize*(increment+1)-2*borderwidth,ystepsize*(increment+2)-2*borderwidth,borderthickness]);
}

for(i=[0:increment-1]){
translate([-towerwidth,0+ystepsize*i,0])cube([towerwidth,ystepsize,zstepsize+zstepsize*i]);  //tower

translate([gdmin+xstepsize*i,0+ystepsize*i,0]) cube([(xstepsize+gdmax-gdmin)-xstepsize*i,ystepsize, zstepsize+zstepsize*i]);  //stairs

translate([gdmin+xstepsize*i,(ystepsize*increment)+ystepsize,0]) cube([(xstepsize+gdmax-gdmin)-xstepsize*i,ystepsize,zstepsize+zstepsize*i]);   //back tower

translate([gdmin+xstepsize*i,0+ystepsize*i,zstepsize+zstepsize*i-bridgethickness]) cube([xstepsize,ystepsize*(increment+1)-ystepsize*i,bridgethickness]);   //bridge
}

for(j=[increment:increment+1]){
translate([-towerwidth,ystepsize*j,0])cube([towerwidth,ystepsize,zstepsize+zstepsize*(increment-1)]);  //tower addon

translate([gdmin+xstepsize*increment,ystepsize*j,0]) cube([(xstepsize+gdmax-gdmin)-xstepsize*increment,ystepsize, zstepsize+zstepsize*(increment-1)]);   //top stair
}

}
