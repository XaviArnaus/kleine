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

# Resources

## Sense HAT
https://www.waveshare.com/wiki/Sense_HAT_(B)