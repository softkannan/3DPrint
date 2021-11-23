/**
 * Marlin 3D Printer Firmware
 * Copyright (C) 2016 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (C) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

// Thermistor Table Template by DaHai

// First Value in the 'OV(   )' is the Resistance, or ADC, value
// Second Value is the Temperature Reported by the Thermocouple on your Multimeter

// Set the Hot-End Temperatue to the preset value in the Second column, wait for
// the temperature to stabilize then insert the ADC value from Pronterface into
// the first column and change the Second Column temperature value to the actual 
// temperature reading from the Thermocouple on your Multimeter
// Repeat until all values below 255c are filled in and replaced.

// Temperatures above 250c are estimates as it is dangerous to heat the hot-end 
// beyond that if it has PTFE (Teflon) in the throat down into the heater block.
// 
// Feel free to replace my OV(  ) estimates with your estimates own based on the
// lower temperature readings. These values help Marlin deterime if a Thermal 
// Runaway condition has occured so it can shut down the heaters to prevent a fire.

// Enable this line if your Marlin source is 1.1.7 or older or you receive a compile
// error that OV is Undeclared
//#define OV OVERSAMPLENR*

const short temptable_99[][2] PROGMEM = {
  { OV(  23), 300 },
  { OV(  25), 295 },
  { OV(  27), 290 },
  { OV(  28), 285 },
  { OV(  31), 280 },
  { OV(  33), 275 },
  { OV(  35), 270 },
  { OV(  38), 265 },
  { OV(  41), 260 },
  { OV(  44), 255 }, 
  { OV(    ), 250 }, 
  { OV(    ), 245 }, 
  { OV(    ), 240 }, 
  { OV(    ), 235 },
  { OV(    ), 230 }, 
  { OV(    ), 225 }, 
  { OV(    ), 220 }, 
  { OV(    ), 215 }, 
  { OV(    ), 210 }, 
  { OV(    ), 205 }, 
  { OV(    ), 200 }, 
  { OV(    ), 195 }, 
  { OV(    ), 190 }, 
  { OV(    ), 185 }, 
  { OV(    ), 180 }, 
  { OV(    ), 170 }, 
  { OV(    ), 160 }, 
  { OV(    ), 150 }, 
  { OV(    ), 140 }, 
  { OV(    ), 130 }, 
  { OV(    ), 120 }, 
  { OV(    ), 110 }, 
  { OV(    ), 100 }, 
  { OV(    ),  90 }, 
  { OV(    ),  80 }, 
  { OV(    ),  70 }, 
  { OV(    ),  60 }, 
  { OV(    ),  50 }, 
  { OV(    ),  40 }, 
  { OV(    ),  30 }  
};
