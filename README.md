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

## Python

## Poetry
```
curl -sSL https://install.python-poetry.org | python3 -
```

# Issues

## I2C device detected but smbus2 error
Post with similar issue, but seems I can solve it the same way:
https://forums.raspberrypi.com/viewtopic.php?t=329882
Keeping the link to know how to define extra buses, for too many devices connected.


```
xavier@kleine:~ $ i2cdetect -y 0
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
xavier@kleine:~ $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- 0c -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- 29 -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- 5c -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- 6b -- -- -- --
```

So seems like I have all at the bus 1. The `ICM20948` class defines bus 1
```
self._bus = smbus.SMBus(1)
```

### Answer
The official Waveshare docs say that the ICM20948 shows up at 0x68, but the reading above suggests 0x6b. Changed and works!

## ZeroDivisionError: float division by zero
```
File "/home/xavier/kleine/kleine/lib/utils/ICM20948.py", line 328, in imuAHRSupdate
    norm = float(1/math.sqrt(mx * mx + my * my + mz * mz))
```
https://forums.raspberrypi.com/viewtopic.php?t=346521

## I have SENSOR(C)!!!
```
wget https://files.waveshare.com/upload/0/04/Sense_HAT_C_Pi.zip
unzip Sense_HAT_C_Pi.zip -d Sense_HAT_C_Pi
```


# Resources

## Sense HAT
https://www.waveshare.com/wiki/Sense_HAT_(B)