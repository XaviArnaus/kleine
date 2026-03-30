# Kleine

Raspbeery PI Zero 2W as a GPS tracker and something more, related to sensors and so on.

First version had a Waveshare Sensor HAT, a Beitian BN-880, a PiSugar UPS and a 2" LCD display, plus 3 physical buttons.
Second version had the Beitian BN-880, a Geekworkm X306 UPS and a Waveshare 1.33" LCD HAT that contained a joystic style input and 3 buttons (So, no Waveshare Sensor HAT, mainly)

The idea is to have a small device that does some sensor logging

# Install
Reviewed working on April 2026 for Second version.

## System

### First start

Most of these steps are optional, and depend on what are the features that you want **Kleine** to support. Sensors, Displays, UPSs and so on usually need to have activated the SPI, I2C and xxx interfaces, and maybe to add some overlays or extra config in `/boot/firmware/config.txt`. I mention all here, and you simply jump whatever does not fit in your setup.

#### Ensure Network connectivity and access (optional)

Once we know what is the IP of the host (check your router, or use tools like `arpscan` to find it out).

1. Add your development SSH Key into the RPi host, to avoid having to type your password every time. More info [here](https://xavier.arnaus.net/blog/set-up-the-ssh-key-authentication-between-hosts)
2. Add the RPi host's SSH Key into GitHub SSH Keys if needed, to be able to clone the repo later on.
3. Add a new Wifi connection relating to your phone's hotspot, so that you can use Pitxu on the go. Use `nmtui` for it.

#### Update the system to the latest version

This is important as some of the hardware - software interconnections are quite edgy and improvements and bugfixes appear often.

```
sudo apt update
sudo apt full-upgrade
sudo rpi-eeprom-update -a
sudo reboot
```

#### Post-installation in `raspi-config`

We need to do some post installation setup through the RPi configuration tool:
```
sudo raspi-config
```

Skip whatever that does not fit to the hardware that you may have connected.

1. Activate the SPI interface under `3 Interface Options > I4 SPI`
2. Activate the I2C interface under `3 Interface Options > I5 I2C`
3. Configure the system Locale under `5 Localisation Options > L1 Locale`

And reboot again.

```
sudo apt install python3-dev swig liblgpio-dev i2c-tools
```

## GPS
The GPS is a Beitian BN-880. 
In the first setup the magnetometer was not connected (SDA SCL) because we already had one up and working in the Sense HAT. Therefore, only the VCC, GND, RX and TX are connected.
In the second setup the magnetometer is connected because we don't have the Sense HAT, so all cables are connected:

Please remember that the TX and RX cables from the GPS must be connected to the opposite RX and TX GPIO pins in the Raspberry Pi:

- GPS RX -> GPIO TX
- GPS TX -> GPIO RX

### Software setup

Set it up through `sudo raspi-config` > Interfaces > Serial and answer:
- "No" to the first question
- "Yes" to the second question

so that the summary is presented like:
```
The serial login shell is disabled
The serial interface is enabled
```

Next thing is to deactivate bluetooth so that the full UART is available. 
By default, the Raspberry Pi 3 Model B (and Zero 2 W) assigns ttyS0 to GPIO14:15 while ttyAMA0 serves the Bluetooth module. As the mini UART is not a full featured UART, you may want to use ttyAMA0 on GPIO14:15 instead as it is a full featured UART
the Mini-UART has one big pitfall. It doesn't have its own clock source, so the UART bitrate depends on the CPU clock. Which means you have to set a fixed CPU clock for reliable communication.

Edit the `/boot/firmware/config.txt` and add the following line at the top of the file:

```
dtoverlay=pi3-disable-bt
```

This frees the `/dev/ttyAMA0` device.

Next, ensure that there is no service enabled nor started relating to the serial ports:

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

They both need to be disabled and stopped, otherwise it continues to revert all permission changes to "only root and no other group is allowed"

Then add your user into the `tty` and `dialout` groups:

```
sudo usermod -a -G dialout user
sudo usermod -a -G tty user
```

Then make the `/dev/ttyAMA0` available for the current user to be read without sudo, by changing its group and the file permissions:

```
sudo chown root:dialout /dev/ttyAMA0
sudo chmod 660 /dev/ttyAMA0
```

The last step is to install the UART monitoring:

```
sudo apt-get install minicom
```

And finally reboot.

With this, we should be able to see the GPS messages flowing throught the GPS without `sudo` required:

```
cat /dev/ttyAMA0
```

Once we can see the messages in the tty file, we need to ensure that the Kleine configuration (`config/gpio.yml`) is reading the right file:

```
serial_port: "/dev/ttyAMA0"
```

## Display

This project relies on having a ST7789 display driver, so both 2" LCD display and the Waveshare 1.33 display and buttons HAT works out of the box.

Just ensure that you defined the right display pixel size and the right rotation that fits your device and setup, by editing the `config/displays.yml`

- First setup: 2" LCD: 320x240, rotate 180 degrees
- Second setip 1,33" LCD: 240x240, rotate 90 degrees

## Buttons

This project relies on having 3 buttons to navigate and behave with the app. 

The first setup had these buttons physically added as GPIO sensors
```
  buttons:
    - name: yellow
      pin: 16
      mocked_as: "tab"
    - name: green
      pin: 26
      mocked_as: "enter"
    - name: blue
      pin: 5
      mocked_as: "space"
```

The second setup uses the buttons embedded in the HAT. It also have defined the joystick buttons, hoping to evolve the app to use them instead of the ones in the first setup:
```
  buttons:
    - name: yellow
      pin: 21
      mocked_as: "tab"
    - name: green
      pin: 16
      mocked_as: "enter"
    - name: blue
      pin: 20
      mocked_as: "space"
    - name: up
      pin: 6
      mocked_as: "up"
    - name: down
      pin: 19
      mocked_as: "down"
    - name: left
      pin: 5
      mocked_as: "left"
    - name: right
      pin: 26
      mocked_as: "right"
    - name: center
      pin: 13
      mocked_as: "shift"
```

## UPS

The first setup had a PiSugar UPS that has a i2c interface to interact with battery info. Be sure to set up the right address so it can communicate:
```
  hardware:
    # [String] I2C Bus
    bus: 1
    # [Int] I2C Address
    address: 0x43
```

The second setup had a Geekworm UPS that does not have any interface with the battery info, so be sure to disable the feature.

## Install system depencencies

Here we setup the application and its dependencies. These can be also at Linux level to support the interaction with the hardware. Most of the times it comes dictates by the code approach and which libraries it uses, so if you feel more confortable with other backend, go to the code and make it happen, and send me a Pull Request to include the support!

### Initial Linux basic setup

The following is initially required:

#### Install Git

```
sudo apt install git
```

### Debian packages to support the Python application

The following are the system dependencies that are needed at OS level so that the Python application works.

#### ❗️ All Linux/Debian code dependencies in one line

Debian packages can be installed all at once. Just make sure that I did not forget to add in this line anything from the below sections, I'm just putting them all together here.

```
sudo apt install python3-dev libjpeg-dev zlib1g-dev libfreetype6-dev swig liblgpio-dev i2c-tools
```

#### Ability to build other dependencies: `python3-dev`

Some dependencies are built at installing time. Please have the `python3-dev` pachage installed beforehand:

```
sudo apt install python3-dev
```

#### Related to `Pillow`

This is needed for the internal Pillow support, we interact with the displays by drawing images.

```
sudo apt install libjpeg-dev zlib1g-dev libfreetype6-dev
```

#### Related to `lgpio`

This is needed for the internal GPIO support

```
sudo apt install swig liblgpio-dev
```

#### Related to `i2c`

This is not needed for the Python / Poetry application to work, but it's useful to debug and identify the own hardware.

```
sudo apt install i2c-tools
```

## Clone the repository

Taking `/home/user/` as a target for the project.

```
git clone git@github.com:XaviArnaus/kleine.git
```

## Poetry
```
curl -sSL https://install.python-poetry.org | python3 -
```

Remember to add the `poetry` path into PATH, inside `.bashrc`:
```
export PATH="/home/user/.local/bin:$PATH"
```

## Ininitalize the project

This creates the Python Virtual Environment and installs / builds all the Python packages required by the application.

```
make init
```

If it complains about the `python.lock`, use `make update` instead.


## Generate all the config files out of the `dist` example ones

```
for file in config/*.yaml.dist; do cp "$file" "${file%.dist}"; done
```

... and edit it at your wish (review the hardware notes at the top of this file)

## Setup Kleine as a service of the system

Adding Kleine as a service allows the RPi to automatically start Kleine on start by itself.
Use the Kleine binary to create the necessary links from the Kleine service definition to the actual Systemd services location.
It will also place links for the shutdown and reboot that clean properly the system when closing it.
```
kleine link_service
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

## Waveshare 1.3 inch LCD HAT
https://www.waveshare.com/wiki/1.3inch_LCD_HAT