For some reason, noone's posted their flash commands yet. I hope this will help people in the same situation.

I've struggled for 2 days with my board, which came without firmware and bootloader. Flashing didn't work, communication wasn't possible (USB wasn't even recognized), so I suspected a bootloader problem very early. I then hooked up some debugger (a black magic probe) and could run the software (via pio debug, just had to set a few things in the platformio.ini), however nothing else worked, and I was left with a board that I could only run by starting the software from another computer. A super annoying situation, especially since I had a brand new board.

I sourced an ST-Link v2 from a friend, and started working on the issue. After hooking it up to the SWD port on the board (luckily there's such a port, there's no other means for debugging, such as a UART interface for serial comunication) with four jumper cables (GND, 3.3V, SWDIO and SWCLK, make sure it's correct or the board won't be found!), I was able to flash the bootloader + firmware from the zip archive provided above.

For flashing on Linux, I can recommend using stlink, a free/open source tool that can flash STM32 chips over SWD. I struggled a bit finding the start address, which is very important if you have .bin files and not .hex (the latter provides such information already). With the wrong start address, st-flash just prints Unknown memory region, which doesn't really help.

The following command worked, flashing went pretty uneventful:

> st-flash write firmware-bigtreetech-e3-dip-stock-with-bootloader.bin 0x8000000
st-flash 1.5.1-47-g2901826
2019-11-04T15:21:45 INFO common.c: Loading device parameters....
2019-11-04T15:21:45 INFO common.c: Device connected is: F1 High-density device, id 0x10036414
2019-11-04T15:21:45 INFO common.c: SRAM size: 0x10000 bytes (64 KiB), Flash: 0x80000 bytes (512 KiB) in pages of 2048 bytes
2019-11-04T15:21:45 INFO common.c: Ignoring 279996 bytes of 0xff at end of file
2019-11-04T15:21:45 INFO common.c: Attempting to write 244292 (0x3ba44) bytes to stm32 address: 134217728 (0x8000000)
Flash page at addr: 0x0803b800 erased
2019-11-04T15:21:47 INFO common.c: Finished erasing 120 pages of 2048 (0x800) bytes
2019-11-04T15:21:47 INFO common.c: Starting Flash write for VL/F0/F3/F1_XL core id
2019-11-04T15:21:47 INFO flash_loader.c: Successfully loaded flash loader in sram
120/120 pages written
2019-11-04T15:21:57 INFO common.c: Starting verification of write complete
2019-11-04T15:21:59 INFO common.c: Flash written and verified! jolly good!
The start address 0x8000000 is where the bootloader starts. It occupies 0x4000 bytes (16kiB), so naturally, the actual firmware starts at 0x8004000. Since we need the bootloader as well, we need to flash it there. You can just flash the bootloader if you plan to use your own firmware, too, it's sufficient.

It's disappointing @bigtreetech didn't chime in in this discussion, providing the missing bootloader + firmware and instructions. @bigtreetech your boards are praised on the Internet, I hope your quality assurance is going to be improved. Boards without a firmware are one thing, but boards without a bootloader are really annoying. You need to invest time and money in order to fix them, and that shouldn't be required.

P.S.: Huge thanks to @thubot for providing the original firmware. I suspect you read it out with an ST-Link v2 programmer as well. After finding the right command, I could flash it just fine with an ST-Link v2 and stlink. The bootloader then worked as intended, flashing a custom Marlin build worked fine from the SD card, the blue LED was flashing just fine, the file was renamed and after fixing my Marlin config, I could communicate with the board via USB and a serial console (using the excellent tio, which I can really recommend for serial communication, it's a life saver!) as expected. I'm going to plug everything in again and will try it out asap!

P.P.S.: @Piscanc try my instructions on a Linux computer (a live CD will work just fine), I hope you can get your board flashed as well.

P.P.P.S.: If you don't have an ST-Link v2 and don't want to invest 2-3 bucks for a cheap Chinese one, please look for the next FabLab or Hackerspace, they most likely have one and they can probably help you flashing it!