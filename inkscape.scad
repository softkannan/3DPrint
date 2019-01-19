module extrude_hook(h, offset = 0.25)
{
  points = [[-3,-3],[3,-3],[3,-1],[5,-1],[5,0.2],[1.5,3],[-1.5,3],[-5,0.2],[-5,-1],[-3,-1]];
  pointsOffset = [[-offset,-offset],[offset,-offset],[offset,-offset],[offset,-offset],[offset,offset],[offset,offset],[-offset,offset],[-offset,offset],[-offset,-offset],[-offset,-offset]];
  
  newPoints = points - pointsOffset;
  
  linear_extrude(height=h)
      polygon(newPoints);
}

union()
{
translate([5,5,6.5])
rotate([90,0,0])
extrude_hook(5);

linear_extrude(2)
square([10,5]);

translate([2.25,0,2])
#linear_extrude(2)
square([5.5,5]);
}
