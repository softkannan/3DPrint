//—————————————————————————
//►►► define overall box dimensions ◄◄◄
  box_length = 80;  //total box length
  box_width = 60;   //total box width
  box_height = 40;  //total box height including rim
  cornerL_cross_section = 6; //cross section of corner pcs
  rim_thickness = 6; //thickness (height) of top rim (slot_depth+1 minimum)
//—————————————————————————  
  slot_depth = 2.0;  //be careful changing this (2)
  slot_width = 1.2;  //and this... (1.2)
  slot_width_clearance = .4;  //and this... (.4)
  //panel thickness = slot_width - slot_width_clearance
//—————————————————————————
  feet = 2;  //  2=feet  0=no feet
//feet under larger size bottom panels for support. a larger sized bottom panel will "droop" & possibly come out of the slots if loaded down & unsupported.
//—————————————————————————
//▬▬► NOTES & TIPS AT THE END OF FILE ◄▬▬
//—————————————————————————
//changing these below may adversely affect the fit of various parts...
  clearance1 = .2;   //pin hole
  clearance2 = .75;  //extra pin hole depth clearance
  clearance3 = .1;   //slot depth clearance (each side)
//—————————————————————————

//—————————————————————————
//▼▼↓↓↓ choose part to render ↓↓↓▼▼

//  "cornerL_LxH"      need 2 pcs
//  "cornerL_WxH"      need 2 pcs
//  "top_rim"          need 1 pc
//  "panel_side_LxH"   need 2 pcs
//  "panel_side_WxH"   need 2 pcs
//  "panel_bottom"     need 1 pc

//▲▲↑↑↑ choose part to render ↑↑↑▲▲

//▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
  part = "cornerL_LxH";  //◄◄◄ change this ◄◄◄
//▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲


//—————————————————————————
  square_pin_hole = 2.5;  //cubed (don't change)
  pin_offset = 1.0;  //pin offset from corner (don't change)
//—————————————————————————
  cLcross = cornerL_cross_section;
  cornerL_L = box_length - cLcross;
  cornerL_W = box_width - cLcross;
  cornerL_H = box_height - rim_thickness;
  pin_size = square_pin_hole - clearance1;
  pin_hole_depth = square_pin_hole + clearance2;
  slot_length_L = cornerL_L - cLcross + slot_depth*2;
  slot_length_W = cornerL_W - cLcross + slot_depth*2;
  slot_length_H = cornerL_H - cLcross + slot_depth*2;
  slot_length_rim_L = box_length - pin_size*2 - pin_offset*2;
  slot_length_rim_W = box_width - pin_size*2 - pin_offset*2;
  panel_length = box_length - cLcross*2 + slot_depth*2 - clearance3*2;
  panel_width = box_width - cLcross*2 + slot_depth*2 - clearance3*2;
  panel_height = box_height - cLcross - rim_thickness + slot_depth*2 - clearance3*2;
  extra_length = cLcross*.22;  //rim slot extra length
//—————————————————————————
     
     
//—↓—↓—↓— dont change these —↓—↓—↓—
if(part == "cornerL_LxH") {//  ←↓dont change these
    cornerL_LxH();//  ←↓↑dont change these
} else if(part == "cornerL_WxH") {
    cornerL_WxH();//  ←↓↑dont change
} else if(part == "top_rim") {
    top_rim();//  ←↓↑dont change
} else if(part == "panel_side_LxH") {
    panel_side_LxH();//  ←↓↑dont change
} else if(part == "panel_side_WxH") {
    panel_side_WxH();//  ←↓↑dont change
} else if(part == "panel_bottom") {
    panel_bottom();//  ←↑dont change
}//—↑—↑—↑— dont change these —↑—↑—↑—



//—————————————————————————      
//————corner L length & height————
module cornerL_LxH(){
difference(){
union(){
//box length lower (along X axis)
translate([0,0,0])
   rotate([0,0,0])
      color("MediumPurple") 
         cube([cornerL_L,cLcross,5]);
//box length upper (along X axis)
translate([0,0,0])
   rotate([0,0,0])
      color("MediumPurple") 
         cube([cornerL_L,5,cLcross]);
//box height lower (along Y axis)
translate([0,0,0])
   rotate([0,0,0])
      color("MediumPurple") 
         cube([cLcross,cornerL_H,5]);
//box height upper (along Y axis)
translate([0,0,0])
   rotate([0,0,0])
      color("MediumPurple") 
         cube([5,cornerL_H,cLcross]);
//square pin
translate([pin_offset+clearance1/2,pin_offset+clearance1/2,cLcross])
   rotate([0,0,0])
      color("DarkOrchid") 
         cube([pin_size,pin_size,pin_size]);
}        
//top slot for length (along X axis)
translate([cLcross-slot_depth-extra_length/2,5/2-slot_width/2,cLcross-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_L,slot_width,slot_depth]);
//side slot for length (along X axis)
translate([cLcross-slot_depth,cLcross-slot_depth,5/2-slot_width/2])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_L,slot_depth,slot_width]);
//square pin hole for length end (along X axis)
translate([cornerL_L-square_pin_hole-clearance2,pin_offset,pin_offset])
   rotate([0,0,0])
      color("Goldenrod") 
         cube([pin_hole_depth,square_pin_hole,square_pin_hole]);
//top slot for height (along Y axis)
translate([5/2-slot_width/2,cLcross-slot_depth-extra_length/2,cLcross-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_width,slot_length_H,slot_depth]);
//side slot for height (along Y axis)
translate([cLcross-slot_depth,cLcross-slot_depth,5/2-slot_width/2])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_depth,slot_length_H,slot_width]);
//square pin hole for height end (along Y axis)
translate([pin_offset,cornerL_H-square_pin_hole-clearance2,pin_offset])
   rotate([0,0,0])
      color("Goldenrod") 
         cube([square_pin_hole,pin_hole_depth,square_pin_hole]);
     }}
     
    
     
//—————————————————————————
//————corner L width & height————
module cornerL_WxH(){
difference(){
union(){
//box width lower (along X axis)
translate([0,0,0])
   rotate([0,0,0])
      color("Plum") 
         cube([cornerL_W,cLcross,5]);
//box width upper (along X axis)
translate([0,0,0])
   rotate([0,0,0])
      color("Plum") 
         cube([cornerL_W,5,cLcross]);
//box height lower (along Y axis)
translate([0,0,0])
   rotate([0,0,0])
      color("Plum") 
         cube([cLcross,cornerL_H,5]);
//box height upper (along Y axis)
translate([0,0,0])
   rotate([0,0,0])
      color("Plum") 
         cube([5,cornerL_H,cLcross]);
//square pin
translate([pin_offset+clearance1/2,pin_offset+clearance1/2,cLcross])
   rotate([0,0,0])
      color("Orchid") 
         cube([pin_size,pin_size,pin_size]);
}     
//top slot for width (along X axis)
translate([cLcross-slot_depth-extra_length/2,5/2-slot_width/2,cLcross-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_W,slot_width,slot_depth]);
//side slot for width (along X axis)
translate([cLcross-slot_depth,cLcross-slot_depth,5/2-slot_width/2])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_W,slot_depth,slot_width]);
 //square pin hole for width end (along X axis)
translate([cornerL_W-square_pin_hole-clearance2,pin_offset,pin_offset])
   rotate([0,0,0])
      color("Goldenrod") 
         cube([pin_hole_depth,square_pin_hole,square_pin_hole]);
//top slot for height (along Y axis)
translate([5/2-slot_width/2,cLcross-slot_depth-extra_length/2,cLcross-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_width,slot_length_H,slot_depth]);
//side slot for height (along Y axis)
translate([cLcross-slot_depth,cLcross-slot_depth,5/2-slot_width/2])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_depth,slot_length_H,slot_width]);
//square pin hole for height end (along Y axis)
translate([pin_offset,cornerL_H-square_pin_hole-clearance2,pin_offset])
   rotate([0,0,0])
      color("Goldenrod") 
         cube([square_pin_hole,pin_hole_depth,square_pin_hole]);
     }}
     
     
     
//—————————————————————————  
//————top rim——————————————
module top_rim(){   
difference(){
union(){
//box length1 (left)
translate([0,0,0])
   rotate([0,0,0])
      color("SlateBlue") 
         cube([5,box_length,rim_thickness]);
//box length2 (right)
translate([box_width-5,0,0])
   rotate([0,0,0])
      color("SlateBlue") 
         cube([5,box_length,rim_thickness]);
//box width1 (lower)
translate([0,0,0])
   rotate([0,0,0])
      color("SlateBlue") 
         cube([box_width,5,rim_thickness]);
//box width2 (upper)
translate([0,box_length-5,0])
   rotate([0,0,0])
      color("SlateBlue") 
         cube([box_width,5,rim_thickness]);
//square pin1 (lower left)
translate([pin_offset+clearance1/2,pin_offset+clearance1/2,rim_thickness])
   rotate([0,0,0])
      color("DarkSlateBlue") 
         cube([pin_size,pin_size,pin_size]);
//square pin2 (lower right)
translate([box_width-pin_size-pin_offset-clearance1/2,pin_offset+clearance1/2,rim_thickness])
   rotate([0,0,0])
      color("DarkSlateBlue") 
         cube([pin_size,pin_size,pin_size]);
//square pin3 (upper left)
translate([pin_offset+clearance1/2,box_length-pin_size-pin_offset-clearance1/2,rim_thickness])
   rotate([0,0,0])
      color("DarkSlateBlue") 
         cube([pin_size,pin_size,pin_size]);
//square pin4 (upper right)
translate([box_width-pin_size-pin_offset-clearance1/2,box_length-pin_size-pin_offset-clearance1/2,rim_thickness])
   rotate([0,0,0])
      color("DarkSlateBlue") 
         cube([pin_size,pin_size,pin_size]);
}        
//top slot for length1 (left)
translate([5/2-slot_width/2,pin_size+pin_offset,rim_thickness-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_width,slot_length_rim_L,slot_depth]);
//top slot for length2 (right)
translate([box_width-5/2-slot_width/2,pin_size+pin_offset,rim_thickness-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_width,slot_length_rim_L,slot_depth]);
//top slot for width1 (lower)
translate([pin_size+pin_offset,5/2-slot_width/2,rim_thickness-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_rim_W,slot_width,slot_depth]);
//top slot for width2 (upper)
translate([pin_size+pin_offset,box_length-5/2-slot_width/2,rim_thickness-slot_depth])
   rotate([0,0,0])
      color("Yellow") 
         cube([slot_length_rim_W,slot_width,slot_depth]);
     }}  
     
   
     
//————side panel length & height————
module panel_side_LxH(){   
translate([0,0,0])
   rotate([0,0,0])
      color("YellowGreen") 
      cube([panel_length,panel_height,slot_width-slot_width_clearance]);
}  


//————side panel width & height————
module panel_side_WxH(){   
translate([0,0,0])
   rotate([0,0,0])
      color("MediumSeaGreen") 
      cube([panel_width,panel_height,slot_width-slot_width_clearance]);
} 


//————bottom panel————
module panel_bottom(){   
union(){
translate([0,0,0])
   rotate([0,0,0])
      color("OliveDrab") 
      cube([panel_width,panel_length,slot_width-slot_width_clearance]);
    
//bottom panel foot1 (left)
translate([panel_width*.25,panel_length*.5,slot_width-slot_width_clearance+1])
   rotate([0,0,0])
      color("MediumSeaGreen") 
      cube([panel_width*.15,5,feet],center=true);
//bottom panel foot2 (upper)    
translate([panel_width*.5,panel_length*.75,slot_width-slot_width_clearance+1])
   rotate([0,0,0])
      color("MediumSeaGreen") 
      cube([5,panel_length*.15,feet],center=true);
//bottom panel foot3 (right)
translate([panel_width*.75,panel_length*.5,slot_width-slot_width_clearance+1])
   rotate([0,0,0])
      color("MediumSeaGreen") 
      cube([panel_width*.15,5,feet],center=true);
//bottom panel foot4 (lower)
translate([panel_width*.5,panel_length*.25,slot_width-slot_width_clearance+1])
   rotate([0,0,0])
      color("MediumSeaGreen") 
      cube([5,panel_length*.15,feet],center=true);
}}
//       ↓           ↓
//        ↓         ↓
//         ↓       ↓
//          ↓     ↓
//           ↓   ↓
//            ↓ ↓
//             ↓
//————————————————————————————
//——————— extra notes ————————
//————————————————————————————




// I am a beginner at using this program. There are probably easier ways to do what this file does.





//I use .8mm thick PANELS. My prototype box had .8mm PANELS. Even at my absolute MAX SIZE of 140mm cubed for my printer, .8mm PANELS are good enough. I don't see a reason for me to change it, although this file does allow for thicker PANELS if you want.

//slot_width 1.2 - slot_width_clearance .4 gives you .8mm panel thickness

//I print all parts SOLID (no infill) for strength

//— — — — — — — —

//suggested settings:
//(the BEST settings in my opinion)

  //cornerL_cross_section = 6
  //rim_thickness = 6
  //slot_width = 1.2
  //slot_depth = 2.0
  //slot_width_clearance = .4
  //with feet on bottom panel.

//These settings give you a sturdy strong box with .8mm thick panels. It's kinda hard to remove support material from the slots, but once you do it works great even on large boxes with a heavy load.

//— — — — — — — —

//when changing cornerL cross section & slot width/depth, ensure that slots & square pin holes do not intersect & that enough material is left to print a strong part.


//slot_width_clearance & slot_width affect the thickness of PANELS when rendering
  
  
//clearance3 & slot_depth affect the size of PANELS when rendering
  
//— — — — — — — —

//for a smaller, more delicate box:

  //cornerL_cross_section = 5
  //rim_thickness = 5
  //slot_width = 1.0
  //slot_depth = 1.0
  //slot_width_clearance = .2
  //with or without feet

//A shallower slot suitable for smaller boxes but not suitable for heavy loads. With or without feet on the bottom panel. Panels are .8mm thick.

//PANELS MORE EASILY POP OUT OF THE SLOTS WHEN YOU DON'T WANT THEM TO.

  
  
  
  
