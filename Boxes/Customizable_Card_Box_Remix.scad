// Customizable Simple Box
//

// Choose Fix Type
BoxFixType = "None"; // [None:None, Hook:Hook, Ender3:Ender3]
// Choose Box Type
BoxType = "Hinge"; // [Press:PressLid, Hinge:HingeLid]
// Choose Hinge Type
HingeTyp = "Build"; // [Build:Build, Metal:Metal]
// Choose Part
BuildPart = "Box"; // [Both:Both, Box:Box, Lid:Lid]
// Box Innner Length
BoxInnerLength = 65;
// Box Innner Height
BoxHeight = 95;
// Box Width, Add Comma Seperated Values for Multi Compartments
BoxInnerCompartmentWidth = [25];
// Box Lid Height
BoxLidHeight = 20;
// Wall Thickness. Choose carefully so your printer can make at least 2 outlines at the narrowest BuildPart (top of the box and lid). For 0.4 nozzle this should be at least 1.6.
BoxWallThickness = 0.8; // [0.2:.1:10]
// Space between lid and box top. The smaller this parameter will be, the tighter box will close.
LidGap = .5; // [.2:0.05:1.0]

// Calculates the Total Inner Width by counting all the width entires
function sum(v, i=0, j=20) = len(v) > i && i <= j ? v[i] + sum(v, i+1, j) : 0;

totalBoxWidth = sum(BoxInnerCompartmentWidth) + (len(BoxInnerCompartmentWidth) - 1) * BoxWallThickness;
// For Internal Use do not change, it there to OpenSCAD boolean operation to work, small number to create polygons properly
smallOffset = .01;
wallOffset = BoxWallThickness * 2;


module BuildBox() 
{
	// Build Full Box
	difference() 
	{
		// Box outer cube
		cube([BoxInnerLength + wallOffset, totalBoxWidth + wallOffset, BoxHeight + wallOffset - LidGap]);
		// Box inner cube
		translate([BoxWallThickness, BoxWallThickness, BoxWallThickness])
			cube([BoxInnerLength, totalBoxWidth, BoxHeight + smallOffset]); 
			
		if(BoxType == "Press")
		{
			//Build Box Side of Lid Lip
			translate([0, totalBoxWidth + wallOffset, BoxHeight + wallOffset])
				rotate(a = 180, v = [1, 0, 0])
					BuildLid(true);
		}
		else if (BoxType == "Hinge")
		{
			//Cutout Top for openning
			translate([-smallOffset, -smallOffset, BoxHeight + wallOffset - BoxWallThickness])
				cube([BoxInnerLength + wallOffset + smallOffset * 2, totalBoxWidth + wallOffset + smallOffset * 2, 
				BoxWallThickness + smallOffset]);
		}
	}
	// Build inner partition if box has more compartment
    if (len(BoxInnerCompartmentWidth) > 1)
	{
		for (i=[0:len(BoxInnerCompartmentWidth) - 2])
		{
			translate([BoxWallThickness, 
				BoxWallThickness + sum(BoxInnerCompartmentWidth, 0, i) + i * BoxWallThickness, BoxWallThickness])
				cube([BoxInnerLength, BoxWallThickness, BoxHeight]);
		}
	}
}

module BuildLid(buildMale = false) 
{
	if(BoxType == "Press")
	{
		innerLibBoxOffset = buildMale?1:-1;
		outerLidBoxOffset = buildMale?1:0;
		difference() 
		{
			translate([-smallOffset * outerLidBoxOffset, -smallOffset * outerLidBoxOffset,
				-smallOffset * outerLidBoxOffset])
				cube([BoxInnerLength + wallOffset + 2 * smallOffset * outerLidBoxOffset, 
					totalBoxWidth + wallOffset + 2 * smallOffset * outerLidBoxOffset, BoxLidHeight + smallOffset]);
			translate([BoxWallThickness / 2 + LidGap / 2 * innerLibBoxOffset,
				BoxWallThickness / 2 + LidGap / 2 * innerLibBoxOffset, BoxWallThickness])
				cube([BoxInnerLength + BoxWallThickness - LidGap * innerLibBoxOffset, 
					totalBoxWidth + BoxWallThickness - LidGap * innerLibBoxOffset, BoxLidHeight]);
		}
	}
	else if (BoxType == "Hinge")
	{
		difference() 
		{
			// Box outer cube
			cube([BoxInnerLength + wallOffset, totalBoxWidth + wallOffset, BoxLidHeight + wallOffset - LidGap]);
			// Box inner cube
			translate([BoxWallThickness, BoxWallThickness, BoxWallThickness])
				cube([BoxInnerLength, totalBoxWidth, BoxLidHeight + smallOffset]); 
			//Cutout Top for openning
			translate([-smallOffset, -smallOffset, BoxLidHeight + wallOffset - BoxWallThickness])
				cube([BoxInnerLength + wallOffset + smallOffset * 2, 
				totalBoxWidth + wallOffset + smallOffset * 2, BoxWallThickness + smallOffset]);
		}
	}
}

if (BuildPart == "Box")
{
	translate([-BoxInnerLength / 2 - BoxWallThickness, -totalBoxWidth / 2 - BoxWallThickness, 0])
		BuildBox();
}
else if (BuildPart == "Lid")
{
	translate([-BoxInnerLength / 2 - BoxWallThickness, -totalBoxWidth / 2 - BoxWallThickness, 0])
		BuildLid();
}
else 
{
	translate([-BoxInnerLength / 2 - BoxWallThickness, -totalBoxWidth - wallOffset - 5, 0])
		BuildBox();
	translate([-BoxInnerLength / 2 - BoxWallThickness, 5, 0])
		BuildLid();
}