## How to perfect your first layer height with Klipper

There are two steps to getting your first layer height perfect. First is **Z endstop calibration**, which gets you most of the way there, then comes **"baby stepping"** to perfect it during a print.
 
Baby stepping is not always necessary, sometimes you will get satisfactory results from Z endstop calibration alone.

### Z ENDSTOP CALIBRATION
   
Do this with your bed at your desired print temp. Heat soak your bed for 10-30 min. 
   1) Home, QGL, then home again (i.e. `G32`). 
   2) Move your nozzle to the center of the build plate. 
   3) Run `Z_ENDSTOP_CALIBRATE` to enter adjustment mode. 
   4) Place a piece of printer paper under the nozzle.
   5) Adjust your nozzle height using `TESTZ Z= ` commands until you just start feeling resistance when moving the paper. 
         - I recommend doing this in 0.025 increments (`TESTZ Z=0.025` and `TESTZ Z=-0.025`). 
         - You can start with coarser moves until you are visibly close, then use small increments.
   6) Run `TESTZ Z=-0.1` (this adjusts for the thickness of the paper)
   7) Run `ACCEPT`.
   8) Run `SAVE_CONFIG`.  This will save your new value and restart Klipper. 
         - Make sure to re-open the config if you have it open in any editors, so that you don't accidentally save over it with the old values.

### BABY STEPPING

This involves running a print, observing the first layer going down, and adjusting your Z offset ("baby stepping") up and down until you have the perfect level of squish. This is easier with an LCD but can also be done without.

Determining your offset value
With an LCD:

1) Edit your `menu.cfg` file. We want to change the baby steps to be a little finer. Search for the "Offset Z" entry and change "input_step" to 0.025. 
2) Run `RESTART`.
3) Go to the "tune" menu of your LCD during your print and adjust until satisfied. Note the value.

Without an LCD:

1) (Optional) Create macros in your printer.cfg file so the commands are easier to remember/run:
		 
```sh
[gcode_macro ZUP]
gcode:
    SET_GCODE_OFFSET Z_ADJUST=0.025 MOVE=1

[gcode_macro ZDOWN]
gcode:
    SET_GCODE_OFFSET Z_ADJUST=-0.025 MOVE=1
```

2) Run `ZUP` and `ZDOWN`  until you have perfected your squish.
	- Or run the associated `SET_GCODE_OFFSET` command if chose not to use the macros.
3) Run GET_POSITION and look for "gcode base". Note the Z value.
	- Alternatively, you can just count how many times you stepped up/down.

Saving your offset value

1) Take your noted Z offset value and subtract it from "position_endstop" at the bottom of your config file. 
	- Increasing this value increases squish, and decreasing it decreases squish. 
2) Save your new value and run `RESTART`.
	- It says "DO NOT EDIT THIS BLOCK OR BELOW"... just ignore that. Or you can move your position_endstop up to your main `[stepper_z]` section if you desire.


### Setting up for the first time stepper_z position_endstop

1) Set bed to 105°C   Nozzle to 200°C and Heatsoak for for 20-30 mins.

2) `G28 XYZ` home the printer

3) Move nozzle to `X150 Y150 Z2`  (I have a 300mm³)

4) run `Z_ENDSTOP_CALIBRATE`  (which adjusts stepper_z position_endstop variable

5) Step down gradually using `TESTZ Z=-XX` until my 0.05mm feeler gauge has a tiny bit of friction then move down 0.05mm (to account for the gauge thickness)

6) `ACCEPT`  (which confirms my new nozzle position as Z=0)

7) Move up 5mm or so (so I don't damage PEI) then `SAVE_CONFIG` to save to config file

