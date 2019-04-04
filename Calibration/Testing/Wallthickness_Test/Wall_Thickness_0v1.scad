//100x100 build platform for debug
translate([-50,-50,-1.01]) %cube([100,100,1]);

BaseThickness=0.5;  //~2 layers
FeatureHeight=3;
//======================================================================================
BarZCenter=BaseThickness+FeatureHeight/2;
//======================================================================================
module test_bar_set(FeatureThickness)
  {
  translate([0,13,BarZCenter]) cube([FeatureThickness,6,FeatureHeight],center=true);
  difference()
    {
    translate([0,3,BarZCenter]) cylinder(r=4,h=FeatureHeight,center=true,$fn=180);
    translate([0,3,BarZCenter]) cylinder(r=4-FeatureThickness,h=FeatureHeight+0.1,center=true,$fn=180);
    }
   translate([0,-9,BarZCenter]) rotate(-45) cube([FeatureThickness,7,FeatureHeight],center=true);
   translate([0,-9,BarZCenter]) rotate(+45) cube([FeatureThickness,7,FeatureHeight],center=true);
  }  
//====================================================================================== 

// 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9
for ( X = [-3:3] )
  translate([X*9.5,15,0]) test_bar_set(0.3+(X+3)*0.1);

// 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2
for ( X = [-3:3] )
  translate([X*9.5,-20,0]) test_bar_set(1+(X+3)*0.2);

//Slide a base under it.
translate([-35,-37,0]) color([0,1,0,0.5]) cube([70,74,BaseThickness]);
//====================================================================================== 

