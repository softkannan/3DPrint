                   .:                     :,                                          
,:::::::: ::`      :::                   :::                                          
,:::::::: ::`      :::                   :::                                          
.,,:::,,, ::`.:,   ... .. .:,     .:. ..`... ..`   ..   .:,    .. ::  .::,     .:,`   
   ,::    :::::::  ::, :::::::  `:::::::.,:: :::  ::: .::::::  ::::: ::::::  .::::::  
   ,::    :::::::: ::, :::::::: ::::::::.,:: :::  ::: :::,:::, ::::: ::::::, :::::::: 
   ,::    :::  ::: ::, :::  :::`::.  :::.,::  ::,`::`:::   ::: :::  `::,`   :::   ::: 
   ,::    ::.  ::: ::, ::`  :::.::    ::.,::  :::::: ::::::::: ::`   :::::: ::::::::: 
   ,::    ::.  ::: ::, ::`  :::.::    ::.,::  .::::: ::::::::: ::`    ::::::::::::::: 
   ,::    ::.  ::: ::, ::`  ::: ::: `:::.,::   ::::  :::`  ,,, ::`  .::  :::.::.  ,,, 
   ,::    ::.  ::: ::, ::`  ::: ::::::::.,::   ::::   :::::::` ::`   ::::::: :::::::. 
   ,::    ::.  ::: ::, ::`  :::  :::::::`,::    ::.    :::::`  ::`   ::::::   :::::.  
                                ::,  ,::                               ``             
                                ::::::::                                              
                                 ::::::                                               
                                  `,,`


https://www.thingiverse.com/thing:2729076
Smart compact temperature calibration tower by gaaZolee is licensed under the Creative Commons - Attribution - Share Alike license.
http://creativecommons.org/licenses/by-sa/3.0/

# Summary

Yet another temperature calibration tower. It suppose to be smart, compact and fulfill several purposes.
* it is functioning as a regular temperature tower
* it contains several test patterns like
    * **overhangs** from 60 deg to 25 deg
    * **bridges** from 15 mm - 30 mm
    * **stringing** test 
    * **curvy** shapes

One floor is exactly *10 mm* and stand is *1.4 mm*. Optimized for *0.2 mm* layer height.

**Note:** STEP models have been added of a plain floor, 000 Floor and the stand.

# Print Settings

Printer Brand: Prusa
Printer: i3 MK2S
Supports: No
Resolution: 0.2 mm
Infill: 15%

Notes: 
Correct temperatures have to be setup in the generated gcode.
It can be easily done in [Slicr3d Prusa edition min. v 1.38.5](https://github.com/prusa3d/Slic3r/releases/tag/version_https://github.com/prusa3d/Slic3r/releases/tag/version_1.38.5)

*Printer Settings -> Custom G-code -> Before layer change G-code*
correct  macro needs to be setup. It should look like

`{if layer_z==1.6}; T tower floor 1`
`M104 S250`
`{elsif layer_z==11.6}
...`

It specifies different temperature for each temperature tower floor.

There are 2 *txt* files included in the project one for PLA and one for ABS towers with the correct macro.
* *ABS_t_tower_before_layer_change_macro.txt*
* *PLA_t_tower_before_layer_change_macro.txt*

Content can be easily copy pasted.

# How to use it?

There is 4 complete temperature towers
* *PLA 180C - 225C*
* *PLA Plus 195C - 235C*
* *ABS 200C - 250C*
* *PETG 220C - 265C

These can be used as they are. Don't forget to setup correct temperatures. See the section above.

There are also separated modules for temp floors from *170C* to  *265C* with *5C* step and a stand.  New heat tower can be easily combined out of them.


# Why another new temperature tower?

I started with 3d printing by may of 2017. I wanted to learn as much as possible in the shortest possible time and speed up configuration of my printer as much as possible. Print out long lasting temperature towers and then other testing shapes was too long to me. So I decided to create a new heat tower which is as compact as possible, serves many basic quality test purposes too and printing take as short time as possible.

I am using it as a basic temperature setup guidance for different filaments. It sped up my setups at least 3 - 4 times. One print instead of 3 - 5.

Currently I am bringing it to you. Enjoy it and I am looking forward to reading any feedback.