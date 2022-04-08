## Klipper Printer Bring up

1) check your x/y endstops work. then tune them so they trigger right before the limit. 

2) with your finger, check your z endstop and make sure that triggers you can do these by doing query_endstops when/when not triggered

3) run G28 X Y to home x and y. now you can use G0/G1 to move x/y around. 

4) move progressively closer to 0,0 manually until you get to the front-left of the bed (or until you get right before it hits the idlers. use get_position to see where it thinks you are, then use that to adjust your max x/y values at the endstops and update your config. 

5) restart after saving your config, then G28 X Y again, then G0 X0 Y0 to see if it goess to the opposite corner now your goal is to get z homed. 

6) enable force_move in config (see example-extras.cfg and extra gcode docs for comments about this). 

7) use G0 moves to get your X and Y somewhere in the rear right approximately above your fsr pin. use force moves in Z to lower the gantry little by little until you can tell exactly where the right X and Y coordinates are 

8) update the coordinates for x,y of the fsr pin in your config. restart 

9) G28 to home all three axes. now you want to get gantry leveling working 

10) use G0 moves to get the nozzle in the center of the bed and about 5mm above it 

11) use query_probe to check the status of the inductive probe on the toolhead, it should be open 

12) use G0 moves to lower the gantry small amount each time checking query_probe to see if it triggers. It should trigger at some point before you touch the bed with the nozzle. 

13) now that you've confirmed the probe is working, use G0 to raise your nozzle up enough you can move it around and clear the bed 

14) move to 0,0 and measure your gantry corner, move to 300,300 (or whatever your size) and measure your other gantry corner

15) update config with corners and restart 

16) run G28 to home, and quad_gantry_level to do one pass of gantry leveling 

17) if that works, run quad_gantry_level more times to see if it converges. it will probably take 3-5 times
now you want to set your z offset 

18) set your bed temp to 100, and wait 10 minutes for it to soak. note that you probably want to update the idle timeout in octoprint or klipper so that it won't turn off the heaters and motors if you wait too long 

19) once at temp, redo your G28 and quad_gantry_level until you are converged (max ajustment less than 0.01mm) 

20) use Z_ENDSTOP_CALIBRATE (see https://github.com/KevinOConnor/klipper/blob/9d33ef4061e0ff669bf3dec349cd9b6dbc1576fa/docs/G-Codes.md for more instructions) to figure out your z offset 

21) probably ready to try a test print at this point

