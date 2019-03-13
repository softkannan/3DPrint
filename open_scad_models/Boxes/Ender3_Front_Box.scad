use <./obiscad/attach.scad>
use <./obiscad/bevel.scad>

// Just for presentation purposes
showClosed = 0; // [0:Split, 1:Closed, 2:Open]

// Show parts
showParts = 0; // [0:All, 1:Base, 2:Lid]

// Show Models
showModel = true;

// Outer box width
boxWidth = 200;

// Outer box depth
boxDepth = 100;

// Outer total box height
boxHeight = 35;

// Lid height
lidHeight = 1.2; // [6:100]

// Radius for rounded corners
corner = 0; // [1:40]

// Number of vertical spaces
numSeparatorsX = 2; // [1:20]

// Number of horizontal spaces
numSeparatorsY = 1; // [1:20]

// Outer wall thickness
wallThickness = 1.2;

// Tolerance
tolerance = 0.5;

// Hinge Radius
hingeRad=3;

// Hinge Length
hingeLength=10; // [5:50]

// Hinge barrette radius
hingeBar=1.2;

// Hinge separation from box body
hingeSep=2; // [0:5]

magnetDia = 6;
magnetHeight = 3;

closeTabType = ""; // [None:None, Magnet:Magnet, Hook=Hook]

hingeType = ""; // [None:None, Hinge:Hinge

rpiBase = true;

/* [Hidden] */
wt = wallThickness;
m=2+corner;
hingeTolerance=0.5;
sep = hingeSep;
$fn=60;

rpiX = 86;
rpiY = 58;

il=5;
iw=wt/2-tolerance;
internalWall = 1;

function arduinoModels(arduinoBoard = "Uno") =
	(arduinoBoard =="Uno") ?
		"./Models/arduino_pro_micro.stl" : //Uno
	(arduinoBoard =="Leonardo") ?
		"./Models/arduino_pro_micro.stl" : //Leonardo
	(arduinoBoard=="Due") ?
		"./Models/arduino_pro_micro.stl" : //Due
	(arduinoBoard=="Mega") ?
		"./Models/arduino_pro_micro.stl" : //Mega
	(arduinoBoard=="ProMicro") ?
		"./Models/arduino_pro_micro.stl" : //ProMicro
	""; //invalid arduinoBoard
	
function arduinoHoleLocations(arduinoBoard = "Uno") = 
	(arduinoBoard =="Uno" || arduinoBoard =="Leonardo") ?
		[[2.54, 15.24 ], [17.78, 66.04 ], [45.72, 66.04 ], [50.8, 13.97 ]]: //Uno, Leonardo holes
	(arduinoBoard=="Due") ?
		[[2.54, 15.24 ],[17.78, 66.04 ],[45.72, 66.04 ],[50.8, 13.97 ],[2.54, 90.17 ],[50.8, 96.52 ]] : //Due Holes
	(arduinoBoard=="Mega") ?
		[[2.54, 15.24 ],[50.8, 13.97 ],[2.54, 90.17 ],[50.8, 96.52 ]] : //Mega holes
	(arduinoBoard=="ProMicro") ?
		[[-1,-1,-1,-1],[-1, 18.4+1,-1,18.4+1],[33.020+1,-1,33.020+1,-1],[33.020+1,18.4+1,33.020+1,18.4+1]] : //Pro Micro holes
	[]; //invalid arduinoBoard
	
//Mounting holes for a Arduino of the specified version
//	Parameters
//		arduinoBoard: the version of the arduinoBoard to generate holes for
//		depth: the depth of the holes in mm
module arduinoHoles (arduinoBoard, mountType = "Mount", depth = 5, mountDia = 6.8, hd = 2.8) 
{
	hr = hd/2;
	
	arduinoDim = arduinoBoardDim(arduinoBoard);

	//preview of the piBoard itself
	if(showModel)
	{
		color("Green")
		{
			translate([-arduinoDim[0]/2.0,arduinoDim[1]/2.0,depth + 1])
			rotate([90,0,-90])
			render() import(arduinoModels(arduinoBoard), convexity=3);
		}
	}
	
	//mounting holes
	translate([-arduinoDim[0]/2.0,-arduinoDim[1]/2,wt-0.1])
	for(holePos = arduinoHoleLocations(arduinoBoard)) {
		if(mountType == "Mount")
		{
			difference()
			{
				translate([holePos[0], holePos[1], depth/2]) cylinder(d=mountDia, h=depth, center = true);
				translate([holePos[0], holePos[1], depth/2]) cylinder(d=hd, h=depth, center = true);
			}
		}
		else if (mountType == "Clip")
		{
			difference()
			{
				translate([holePos[0], holePos[1], depth/2]) cube([mountDia,mountDia, depth], center = true);
				translate([holePos[2], holePos[3], depth/2]) cylinder(d=hd, h=depth+0.01, center = true);
			}
		}
	}
}

function arduinoBoardDim (arduinoBoard="Uno") =
	(arduinoBoard=="Uno" || arduinoBoard=="Leonardo") ?
		[68.58, 53.34, 1.25] :
	(arduinoBoard=="Due") ?
		[101.6, 53.34, 1.25] :
	(arduinoBoard == "Mega") ?
		[101.6, 53.34, 1.25] :
	(arduinoBoard == "ProMicro") ?
		[33.020, 18.4, 1.25] :
	[0,0,0];
	
function moduleBoardModels(board = "") =
	(board =="Uno") ?
		"./Models/arduino_pro_micro.stl" : //Uno
	(board =="Leonardo") ?
		"./Models/arduino_pro_micro.stl" : //Leonardo
	(board=="Due") ?
		"./Models/arduino_pro_micro.stl" : //Due
	(board=="Mega") ?
		"./Models/arduino_pro_micro.stl" : //Mega
	(board=="ProMicro") ?
		"./Models/arduino_pro_micro.stl" : //ProMicro
	""; //invalid board
	
function moduleBoardHoleLocations(board = "") = 
	(board =="1A+") ?
		[[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]] : //pi 1B+, 2B, 3B
	(board=="Zero") ?
		[[3.5, 3.5], [61.5, 3.5], [3.5, 26.5], [61.5, 26.5]] : //pi zero
	(board=="1B") ?
		[[80, 43.5], [25, 17.5]] :
	[]; //invalid piBoard
	
function moduleBoardDim (board="3B") =
	(board=="1B") ?
		[85, 56, 1.25] :
	(board=="Zero") ?
		[65, 30, 1.25] :
	(board == "1A+") ?
		[65, 56, 1.25] :
	[0,0,0];
	
//Mounting holes for a Arduino of the specified version
//	Parameters
//		board: the version of the module board to generate holes for
//		depth: the depth of the holes in mm
module moduleBoardHoles (board, mountType = "Mount", depth = 5, mountDia = 6.8, hd = 2.8) 
{
	hr = hd/2;
	
	arduinoDim = moduleBoardDim(board);

	//preview of the piBoard itself
	if(showModel)
	{
		color("Green")
		{
			translate([-arduinoDim[0]/2.0,arduinoDim[1]/2.0,depth + 1])
			rotate([90,0,-90])
			render() import(moduleBoardModels(board), convexity=3);
		}
	}
	
	//mounting holes
	translate([-arduinoDim[0]/2.0,-arduinoDim[1]/2,wt-0.1])
	for(holePos = moduleBoardHoleLocations(board)) {
		if(mountType == "Mount")
		{
			difference()
			{
				translate([holePos[0], holePos[1], depth/2]) cylinder(d=mountDia, h=depth, center = true);
				translate([holePos[0], holePos[1], depth/2]) cylinder(d=hd, h=depth, center = true);
			}
		}
		else if (mountType == "Clip")
		{
			difference()
			{
				translate([holePos[0], holePos[1], depth/2]) cube([mountDia,mountDia, depth], center = true);
				translate([holePos[2], holePos[3], depth/2]) cylinder(d=hd, h=depth+0.01, center = true);
			}
		}
	}
}

function piModels (piBoard="3B") =
	(piBoard=="1B") ?
		"./Models/RPi3BPlus.stl":
	(piBoard=="1B+") ?
		"./Models/RPi3BPlus.stl":
	(piBoard=="2B") ?
		"./Models/RPi3BPlus.stl":
	(piBoard=="3B") ?
		"./Models/RPi3BPlus.stl":
	(piBoard=="Zero") ?
		"./Models/RPi3BPlus.stl":
	(piBoard == "1A+") ?
		"./Models/RPi3BPlus.stl":
	""; //invalid pi
	
//get vector of [x,y] vectors of locations of mounting holes based on Pi version
function piHoleLocations (piBoard="3B") = 
	(piBoard=="1A+" || piBoard=="1B+" || piBoard=="2B" || piBoard=="3B") ?
		[[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]] : //pi 1B+, 2B, 3B
	(piBoard=="Zero") ?
		[[3.5, 3.5], [61.5, 3.5], [3.5, 26.5], [61.5, 26.5]] : //pi zero
	(piBoard=="1B") ?
		[[80, 43.5], [25, 17.5]] :
	[]; //invalid piBoard

//get vector of [x,y,z] dimensions of piBoard
//	dimensions are for PCB only, not ports or anything else
function piBoardDim (piBoard="3B") =
	(piBoard=="1B" || piBoard=="1B+" || piBoard=="2B" || piBoard=="3B") ?
		[85, 56, 1.25] :
	(piBoard=="Zero") ?
		[65, 30, 1.25] :
	(piBoard == "1A+") ?
		[65, 56, 1.25] :
	[0,0,0];
	
//Mounting holes for a Raspberry Pi of the specified version
//	Parameters
//		piBoard: the version of the raspberry pi to generate holes for
//		depth: the depth of the holes in mm
module piHoles (piBoard,depth = 5) {
	hd = 2.8; //radius of pi mounting holes plus a tiny bit extra to account for shrinkage when 3D printing
	hr = hd/2;
	mountDia = 5.8;
	
	rpiDiem = piBoardDim(piBoard);

	//preview of the piBoard itself
	if(showModel)
	{
		color("Green")
		{
			translate([rpiDiem[0]/2.0,rpiDiem[1]/2.0,depth])
			rotate([90,0,180])
			render() import(piModels(piBoard), convexity=3);
		}
	}
	
	//mounting holes
	translate([-rpiDiem[0]/2.0 + 20,-rpiDiem[1]/2,wt-0.1])
	for(holePos = piHoleLocations(piBoard)) {
		difference()
		{
			translate([holePos[0], holePos[1], depth/2]) cylinder(d=mountDia, h=depth, center = true);
			translate([holePos[0], holePos[1], depth/2]) cylinder(d=hd, h=depth+0.01, center = true);
		}
	}
}

box();

module box() 
{
    if( showParts != 2 || showClosed ==1) 
	{
        boxBase();
		if(hingeType == "Hinge")
		{
			separators(numSeparatorsX, numSeparatorsY, boxWidth, boxDepth, boxHeight-wt-1);
		}
    }
    if (showClosed == 1 ) 
	{
        translate([0, 0, boxHeight]) 
			rotate(a=[180, 0, 0]) 
				boxLid();
    }
    else if (showClosed == 2) 
	{
        boxBase();
        translate([0, boxDepth/2+4*hingeRad, boxDepth+hingeRad+sep]) 
			rotate(a=[90, 0, 0]) 
				boxLid();
    }
    else 
	{
        if (showParts != 1)
		{
			translate([boxWidth + 5, 0, 0]) 
				boxLid();
		}
    }
}


module separators (nx, ny, sizeX, sizeY, height) 
{
    xS = sizeX / nx;
    yS = sizeY / ny;
    union()
	{
        if ( nx > 1) 
		{
            for ( a = [0 : nx-2] ) 
			{
                translate([-sizeX/2+xS*(a+1), 0, 0])
                    linear_extrude(height=height)
						square([internalWall, sizeY-2*wt], center = true);
            }
        }
        if ( ny > 1) 
		{
            for ( b = [0 : ny-2] ) 
			{
                translate([0, -sizeY/2+yS*(b+1), 0])
                    linear_extrude(height=height)
						square([sizeX-2*wt, internalWall], center = true);
            }
        }
    }

}

module boxBase() 
{
	if(rpiBase)
	{
		translate([50,15,-0.01])
			piHoles("3B");
	
		translate([70,-30,-0.01])
			arduinoHoles("ProMicro", "Clip");
	}
    difference()
	{
        union()
		{
            roundedCube(boxWidth, boxDepth, boxHeight-lidHeight, corner);
			
			if(closeTabType == "Magnet")
			{
				translate([0, -boxDepth/2-magnetDia / 2, boxHeight-lidHeight-magnetHeight-0.6]) 
					closeInsert();
			}
			
			if(hingeType == "Hinge")
			{
				hingeLow(hingeRad, hingeLength);
				translate([0, 0, boxHeight-lidHeight]) 
					roundedCube(boxWidth-2*(wt-iw), boxDepth-2*(wt-iw), il, corner);
			}
        }
		if(closeTabType == "Hook")
		{
			translate([0, -boxDepth/2-1, boxHeight-lidHeight-5]) 
				closeInsert();
		}
		
        translate([0, 0, wt]) 
			roundedCube(boxWidth-2*wt, boxDepth-2*wt, boxHeight+il, corner);
    }
}


module boxLid() 
{
    closeTab();
    difference() 
	{
		union () 
		{
			if(hingeType == "Hinge")
			{
				roundedCube(boxWidth, boxDepth, lidHeight, corner);
				hingeUp(hingeRad, hingeLength);
			}
			else
			{
				roundedCube(boxWidth, boxDepth, lidHeight, corner);
			}
		}
		if(hingeType == "Hinge")
		{
			translate([0, 0, lidHeight-il]) roundedCube(boxWidth-2*iw, boxDepth-2*iw, il+1, corner);
			translate([0, 0, wt]) roundedCube(boxWidth-2*wt, boxDepth-2*wt, boxHeight, corner);
		}
    } 
}

module arc( height, depth, radius, degrees ) {
    // This dies a horible death if it's not rendered here 
    // -- sucks up all memory and spins out of control 
    render() {
        difference() {
            // Outer ring
            rotate_extrude($fn = 100)
                translate([radius - height, 0, 0])
                    square([height,depth]);
         
            // Cut half off
            translate([0,-(radius+1),-.5]) 
                cube ([radius+1,(radius+1)*2,depth+1]);
         
            // Cover the other half as necessary
            rotate([0,0,180-degrees])
            translate([0,-(radius+1),-.5]) 
                cube ([radius+1,(radius+1)*2,depth+1]);
         
        }
    }
}

module closeTab() 
{
	if(closeTabType == "Hook")
	{
		translate([-5, boxDepth/2+1, lidHeight-5]) 
		{
			rotate(a=[180, 0, 0]) rotate(a=[0, 90, 0]) 
				linear_extrude(height=10) 
					polygon(points=[[10, 0], [8, 2], [8, 1], [-1, 1], [0, 0]]);
		}
	}
	else if(closeTabType == "Magnet")
	{
		translate([-magnetDia / 2, boxDepth/2, lidHeight- magnetDia + 1.2/2]) 
		{
			difference()
			{
				union()
				{
					translate([0,0,1.2])
					linear_extrude( height  = magnetHeight + 1.2)
						offset(r = 1.2) 
						{
							square([magnetDia,magnetDia]);
						}
					translate([0,0,magnetHeight - 0.59])
					minkowski()
					{
						rotate(a=[0,270,180])
						arc(magnetDia,magnetDia,magnetDia,90);
						cylinder(r=1.21,h=1);
					}
				}
				
				translate([magnetDia / 2, magnetDia / 2,magnetHeight - 0.59])
					linear_extrude( height  = magnetHeight)
						circle(d = magnetDia);
				
				//Edge clean
			    translate([-1.21,-1.21,0.01])	
			    linear_extrude( height  = magnetHeight + 1.2 * 2)
					square([magnetDia + 1.21 * 2,1.21]);
			}
		}
	}
}

module closeInsert() 
{
	if(closeTabType == "Hook")
	{
		translate([-15/2, 0, 0.5])
		cube([15, 3, 2]);
	}
	else if(closeTabType == "Magnet")
	{
		difference()
		{
			union()
			{
				translate([0,0,1.5])
					linear_extrude( height  = magnetHeight + 1.2, center = true)
					offset(r = 1.2) 
					{
						square([magnetDia,magnetDia], center = true);
					}
					
				minkowski()
					{
						translate([magnetDia/2,magnetDia/2,0])
						rotate(a=[90,270,270])
						arc(magnetDia,magnetDia,magnetDia,90);
						cylinder(r=1.21,h=1);
					}
				/* difference()
				{
					translate([0,magnetDia / 2,1.5])
					rotate(a=[0,90,0], center = true)		
					cylinder(r=magnetDia, h=magnetDia+1.2 * 2, center = true);
					translate([0,1.2,magnetDia - 1.2 / 2])
					linear_extrude( height  = magnetHeight + 1.2, center = true)
					square([magnetDia + 1.21 * 2,magnetDia + 1.21 * 2], center = true);
				} */
			}
			translate([0,0,0.61])
				linear_extrude( height  = magnetHeight)
					circle(d = magnetDia);
		}
	}
}

module hingeUp(hingeRad, hingeLength) 
{
    rotate(a=[0, 0, 180])
    translate([-boxWidth/2, boxDepth/2, lidHeight])
    rotate(a=[0, 90, 0])
    difference() 
	{
        union() 
		{
        
			if ((hingeLength+hingeTolerance)*6+2*m<boxWidth) 
			{
				translate([0, 0, m+hingeLength+hingeTolerance]) hingeSupport(hingeRad, hingeLength);
				translate([0, 0, boxWidth-2*hingeLength-hingeTolerance-m]) hingeSupport(hingeRad, hingeLength);
			}
			else 
			{
				translate([0, 0, m+hingeLength+hingeTolerance]) 
					hingeSupport(hingeRad, boxWidth-2*m-2*hingeLength-2);
			}
		}
        translate([0, sep+hingeRad, -1]) cylinder(r=hingeBar, h=boxWidth+2);
    }
}

module hingeLow(hingeRad, hingeLength) 
{
    translate([-boxWidth/2, boxDepth/2, boxHeight-lidHeight])
    rotate(a=[0, 90, 0])
    difference() 
	{
        union() 
		{
			translate([0, 0, m])
				hingeSupport(hingeRad, hingeLength);
			if ((hingeLength+hingeTolerance)*6+2*m<boxWidth) 
			{
				translate([0, 0, hingeLength*2+2*hingeTolerance+m]) 
					hingeSupport(hingeRad, hingeLength);
				translate([0, 0, boxWidth-hingeLength*3-2*hingeTolerance-m]) 
					hingeSupport(hingeRad, hingeLength);
			}
			translate([0, 0, boxWidth-hingeLength-m]) 
				hingeSupport(hingeRad, hingeLength);
		}
        translate([0, sep+hingeRad, -1]) 
			cylinder(r=hingeBar, h=boxWidth+2);
    }
}

module hingeSupport(hingeRad, hingeLength) 
{
    translate([0, sep+hingeRad, 0]) 
	{
/*    cylinder(r=hingeRad, h=hingeLength); 
    difference() {
        translate([0, -hingeRad-sep, 0] ) cube([hingeRad*2, hingeRad+1+sep, hingeLength]);
        translate([hingeRad*2, -sep, -1] ) cylinder(r=hingeRad, h=hingeLength+2); 
        translate([hingeRad, hingeRad/2-sep-2, -1] ) cube([hingeRad*2, hingeRad+1+sep, hingeLength+2]);
    }}*/
        cylinder(r=hingeRad, h=hingeLength);
        difference() 
		{
			translate([0, -(hingeRad+sep), 0]) 
				cube([2*hingeRad+sep, sep+hingeRad, hingeLength]);

			translate([hingeRad*2+sep, 0, -1]) 
				cylinder(r=hingeRad+sep, h=hingeLength+2);
		}
    }
}


module roundedCube (w, d, h, r) 
{
	if(r > 0)
	{
		hull() 
		{
			translate([-w/2+r, -d/2+r, 0]) cylinder(r=r, h=h);
			translate([-w/2+r, d/2-r, 0]) cylinder(r=r, h=h);    
			translate([w/2-r, -d/2+r, 0]) cylinder(r=r, h=h);
			translate([w/2-r, d/2-r, 0]) cylinder(r=r, h=h);
		}
	}
	else
	{
		translate([-w/2, -d/2, 0]) cube([w,d,h]);
	}
}