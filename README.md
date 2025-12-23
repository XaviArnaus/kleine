# Kleine

bla

# Install

## System

```
sudo apt install python3-dev swig liblgpio-dev i2c-tools
```

## Sense drivers

### BCM2835
```
sudo apt-get install binutils make csh g++ sed gawk autoconf automake autotools-dev
```

```
#Open the Raspberry Pi terminal and run the following commands:
sudo wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
sudo tar zxvf bcm2835-1.71.tar.gz 
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
# For more information, please refer to the official website: http://www.airspayce.com/mikem/bcm2835/
```

### WiringPi

```
sudo apt-get install libc6
```

May need the following:
```
sudo apt --fix-broken install
```

```
#Open the Raspberry Pi terminal and run the following commands:
cd
sudo apt-get install wiringpi
#For Raspberry Pi systems after May 2019 (those earlier may not require execution), an upgrade may be necessary:
wget https://github.com/WiringPi/WiringPi/releases/download/3.16/wiringpi_3.16_arm64.deb
sudo dpkg -i wiringpi_3.16_arm64.deb
gpio -v
# Run gpio -v and version 2.52 will appear. If it does not appear, there is an installation error
```

### lgpio
```
sudo apt-get install python3-setuptools
```

```
sudo su
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
sudo make install 
# For more information, please refer to the official website: https://github.com/gpiozero/lg
```

## GPS
The GPS is a Beitian BN-880. The magnetometer is not connected (SDA SCL) because we already have one up and working in the Sense Hat. Therefore, only the VCC, GND, RX and TX are connected.

The RPi has already activated the uart in the `/boot/firmware/config.txt`, so with the following
```
sudo cat /dev/serial0
```

...we already see that the GPS is transmitting

The Serial0 service appears to be already disabled:
```
$ sudo systemctl status serial-getty@ttys0.service
○ serial-getty@ttys0.service - Serial Getty on ttys0
     Loaded: loaded (/usr/lib/systemd/system/serial-getty@.service; disabled; preset: enabled)
     Active: inactive (dead)
       Docs: man:agetty(8)
             man:systemd-getty-generator(8)
             https://0pointer.de/blog/projects/serial-console.html
```

and also
```
$ sudo systemctl status serial-getty@ttyAMA0.service
○ serial-getty@ttyAMA0.service - Serial Getty on ttyAMA0
     Loaded: loaded (/usr/lib/systemd/system/serial-getty@.service; disabled; preset: enabled)
     Active: inactive (dead)
       Docs: man:agetty(8)
             man:systemd-getty-generator(8)
             https://0pointer.de/blog/projects/serial-console.html
```

We need to have the first one enabled:
```
sudo systemctl enable serial-getty@ttys0.service
```

So next is to install the Serial monitor to be able to read the NMEA messages
```
sudo apt-get install minicom
```

We can see messages incoming by peeking into the file handler
```
sudo cat /dev/ttyS0
```

I had problems with the permissions of the serial port:
```
$ ll /dev/ttyS0
crw------- 1 root root 4, 64 Dec 19 15:21 /dev/ttyS0
```

Be sure that the Serial is setup properly. The Serial Shell needs to be deactivated but the hardware needs to be activated.

Set it up through `sudo raspi-config` > Interfaces > Serial and answer:
- "No" to the first question
- "Yes" to the second question

so that the summary is presented like:
```
The serial login shell is disabled
The serial interface is enabled
```

Then:
```
$ ll /dev/ttyS0
crw-rw---- 1 root dialout 4, 64 Dec 19 15:22 /dev/ttyS0
xavier@kleine:~/kleine $ kleine
```

## Enable SSH via USB

This is only to be able to connect a USB to a host and accept incoming SSH connections.

https://raspberrypi.stackexchange.com/questions/66431/headless-pi-zero-ssh-access-over-usb

1. Add the overlay in the config
```
sudo nano /boot/firmware/config.txt
```

and add `dtoverlay=dwc2`.

In my case the line was already present at the bottom under the section `[cm5]`. I've moveid it under the `[all]` section

2. Create an empty file in the `/boot` directory called `ssh`
```
sudo touch /boot/ssh
```

3. Tell the RPi to load the dwc2 module at start.
```
sudo nano /boot/firmware/cmdline.txt
```

and add `modules-load=dwc2,g_ether` just right after `rootwait`, with a space. For example, I had:
```
console=tty1 root=PARTUUID=a5f01904-02 rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=DE
```

and I left it as:
```
console=tty1 root=PARTUUID=a5f01904-02 rootfstype=ext4 fsck.repair=yes rootwait modules-load=dwc2,g_ether cfg80211.ieee80211_regdom=DE
```

4. Reboot

⚠️ Didn't work. Abandoning the approach to set up Wifi connections from HotSpots.

## Make the GPS to use the real UART instead of the mini-UART
from https://gist.github.com/EEParker/d91fab4227c5ce4d88ce8a0e4c2df75e

> By default, the Raspberry Pi 3 Model B (and Zero 2 W) assigns ttyS0 to GPIO14:15 while ttyAMA0 serves the Bluetooth module. As the mini UART is not a full featured UART, you may want to use ttyAMA0 on GPIO14:15 instead as it is a full featured UART. Fortunately, there are a couple of device tree overlays that will accomplish this.
>
>pi3-miniuart-bt: This overlay flip flops the UARTs by assigning ttyAMA0 to GPIO14:15 while assigning ttyS0 to the Bluetooth module.
>pi3-disable-bt: This overlay assigns ttyAMA0 to GPIO14:15 while disabling Bluetooth altogether.
>In general, the Mini-UART has one big pitfall. It doesn't have its own clock source, so the UART bitrate depends on the CPU clock. Which means you have to set a fixed CPU clock for reliable communication.

1. Added the `pi3-disable-bt` into `/boot/firmware/config.txt
2. Reboot

Worked out of the box, don't know if it really did anything. I don't see an extra port in `/dev/tty*`

## Python

## Poetry
```
curl -sSL https://install.python-poetry.org | python3 -
```


# Resources

## Sense HAT
https://www.waveshare.com/wiki/Sense_HAT_(C)

## SPI Linux support
Very interesting for the SPIn pinouts
https://elinux.org/RPi_SPI#Hardware

## Overlays for Waveshare stuff
https://github.com/swkim01/waveshare-dtoverlays

## GPS Beitian BN-880
https://store.beitian.com/blogs/news/instructions-and-correct-use-of-gps-module

Datasheet downloaded [here](./vendor/gps/91u96ycpw9L.pdf) from [what the seller uploaded on Amazon](https://m.media-amazon.com/images/I/91u96ycpw9L.pdf)

### NMEA messages
https://swairlearn.bluecover.pt/nmea_analyser
https://www.rfwireless-world.com/terminology/gps-nmea-sentences
https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_GGA.html

https://www.aeanet.org/how-many-gps-satellites-do-you-need/