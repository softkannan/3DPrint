//0.38 mm for Tighter Fit
//0.25 mm for press fit
//0.5 mm for easy fit
$fn=100;
linear_extrude( height= 4)
{

difference()
{
square([50,15],center=true);

translate([-18,0,0])
#circle( r = 5);

translate([-6,0,0])
#circle( r = 5 + (0.38) / 2);

translate([6,0,0])
#circle( r = 5 + (0.25 / 2));

translate([18,0,0])
#circle( r = 5 + (0.5 / 2));
}
}

linear_extrude(height=8)
translate([32,0,0])
circle(r=5);