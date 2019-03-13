
module extrude_hook(h, offset = 0.25)
{
  points = [[-3,-3],[3,-3],[3,-1],[5,-1],[5,0.2],[1.5,3],[-1.5,3],[-5,0.2],[-5,-1],[-3,-1]];
  pointsOffset = [[-offset,-offset],[offset,-offset],[offset,-offset],[offset,-offset],[offset,offset],[offset,offset],[-offset,offset],[-offset,offset],[-offset,-offset],[-offset,-offset]];
  
  newPoints = points - pointsOffset;
  
  linear_extrude(height=h)
      polygon(newPoints);
}

extrude_hook(5);
