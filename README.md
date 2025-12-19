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

### gps
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