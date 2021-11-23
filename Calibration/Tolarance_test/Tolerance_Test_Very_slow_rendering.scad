// Tolerances to test *Must be 7 values*
tolerances = [0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1];

// Object height
pin_height = 10; //[10:20]

// Pin radius
pin_radius = 7.5; //[5:0.5:10]

// Collar clearance
collar_clearance = 1; //[1:0.5:2]

// Hex wrench size (measured across flats)
pin_hex = 6; //[5, 6, 8]

// Font size multiplier
font_size = 85; //[0:5:100]

/* {Hidden] */
pin_hex_r = ((1/cos(30))*(pin_hex/2)*1.05);
separation = (pin_radius + collar_clearance*2 + tolerances[0] + 0.5)*2;
separation_matrix = [[0, 0], [0, 1], [0.866, 0.5], [0.866, -0.5], [0, -1], [-0.866, -0.5], [-0.866, 0.5]];
font_size_factor = 0.65*(font_size/100);
$fn=60*1;

// Make carrier
difference(){
  for (a = [0:6]){ //base shape
    translate([separation_matrix[a][0]*separation, separation_matrix[a][1]*separation, 0])
      cylinder(r=(separation/2)*1.15, h=pin_height);
  }
  for (a = [0:6]){ //remove pins with the appropriate clearances
    translate([separation_matrix[a][0]*separation, separation_matrix[a][1]*separation, 0])
      make_pin(pin_radius+tolerances[a], collar_clearance*2, "", false);
  }
}
// Make pins
for (a = [0:6]){
  translate([separation_matrix[a][0]*separation, separation_matrix[a][1]*separation, 0])
  make_pin(pin_radius, collar_clearance, str(tolerances[a]), true);
}

module make_pin(radius, collar, pin_text = "", hex_key = false) {
  intersection(){
    difference(){
      union(){
        cylinder(r=radius, h=pin_height); //base pin
        translate([0, 0, pin_height/2]){ //collar
          rotate_extrude(convexity = 10)
          translate([radius, 0, pin_height/2])
          circle(r = collar, $fn = 100);
        }
        cylinder(r1=radius+1, r2=radius, h=1); //bottom outward chamfered edge - gets removed on the pins
        translate([0, 0, pin_height-1])
          cylinder(r2=radius+1, r1=radius, h=1); //top outward chamfered edge - gets removed on the pins
      }
      if (hex_key==true) {
        cylinder(r=pin_hex_r, h=(pin_height/2), $fn=6); //hex-wrench cutout
      }
      translate([0,0,pin_height-1]){
        linear_extrude(1) text(text=pin_text, size=pin_radius*font_size_factor, halign="center", valign="center", height=5); //tolerance text
      }
    }
    if (pin_text!=""){ //chamfer pin
      union(){
        translate([0, 0, pin_height/2])
        cylinder(r1=radius+(pin_height/2)-1, r2=radius-2, h=(pin_height/2)+1);
        translate([0, 0, -1])
        cylinder(r2=radius+(pin_height/2)-1, r1=radius-2, h=(pin_height/2)+1);
      }
    }
  }
}
