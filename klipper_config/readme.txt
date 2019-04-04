git clone https://github.com/softkannan/klipper
./klipper/scripts/install-octopi.sh


cd ~/klipper/
make menuconfig

make

sudo service klipper stop
make flash FLASH_DEVICE=/dev/ttyUSB0
sudo service klipper start


cp ~/klipper/config/example.cfg ~/printer.cfg
nano ~/printer.cfg



Update New Software

How do I upgrade to the latest software?
The general way to upgrade is to ssh into the Raspberry Pi and run:

cd ~/klipper
git pull
~/klipper/scripts/install-octopi.sh
Then one can recompile and flash the micro-controller code. For example:

make menuconfig
make clean
make

sudo service klipper stop
make flash FLASH_DEVICE=/dev/ttyUSB0
sudo service klipper start

However, it's often the case that only the host software changes. In this case, one can update and restart just the host software with:

cd ~/klipper
git pull
sudo service klipper restart

If after using this shortcut the software warns about needing to reflash the micro-controller or some other unusual error occurs, then follow the full upgrade steps outlined above. Note that the RESTART and FIRMWARE_RESTART g-code commands do not load new software - the above "sudo service klipper restart" and "make flash" commands are needed for a software change to take effect.