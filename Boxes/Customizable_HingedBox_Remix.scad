// Just for presentation purposes
showClosed = 0; // [0:Split, 1:Closed, 2:Open]

// Show parts
showParts = 1; // [0:All, 1:Base, 2:Lid]

// Outer box width
boxWidth = 150;

// Outer box depth
boxDepth = 100;

// Outer total box height
boxHeight = 100;

// Lid height
lidHeight = 10; // [6:100]

// Radius for rounded corners
corner = 5; // [1:40]

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

closeTabType = "Magnet"; // [Magnet:Magnet, Hook=Hook]

/* [Hidden] */
wt = wallThickness;
m=2+corner;
hingeTolerance=0.5;
sep = hingeSep;
$fn=60;

il=5;
iw=wt/2-tolerance;
internalWall = 1;

box();

module box() 
{
    if( showParts != 2 || showClosed ==1) 
	{
        boxBase();
        separators(numSeparatorsX, numSeparatorsY, boxWidth, boxDepth, boxHeight-wt-1);
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
            hingeLow(hingeRad, hingeLength);
            translate([0, 0, boxHeight-lidHeight]) 
				roundedCube(boxWidth-2*(wt-iw), boxDepth-2*(wt-iw), il, corner);
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
            roundedCube(boxWidth, boxDepth, lidHeight, corner);
            hingeUp(hingeRad, hingeLength);
        }
            
        translate([0, 0, lidHeight-il]) roundedCube(boxWidth-2*iw, boxDepth-2*iw, il+1, corner);
        translate([0, 0, wt]) roundedCube(boxWidth-2*wt, boxDepth-2*wt, boxHeight, corner);
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
    hull() 
	{
        translate([-w/2+r, -d/2+r, 0]) cylinder(r=r, h=h);
        translate([-w/2+r, d/2-r, 0]) cylinder(r=r, h=h);    
        translate([w/2-r, -d/2+r, 0]) cylinder(r=r, h=h);
        translate([w/2-r, d/2-r, 0]) cylinder(r=r, h=h);
    }
}