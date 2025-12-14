# Issues

## ✅ Accelerometer does not work

### I2C device detected but smbus2 error
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

#### Answer
The official Waveshare docs say that the ICM20948 shows up at 0x68, but the reading above suggests 0x6b. Changed and works!

### ZeroDivisionError: float division by zero
```
File "/home/xavier/kleine/kleine/lib/utils/ICM20948.py", line 328, in imuAHRSupdate
    norm = float(1/math.sqrt(mx * mx + my * my + mz * mz))
```
https://forums.raspberrypi.com/viewtopic.php?t=346521

### I have SENSOR(C)!!!
```
wget https://files.waveshare.com/upload/0/04/Sense_HAT_C_Pi.zip
unzip Sense_HAT_C_Pi.zip -d Sense_HAT_C_Pi
```

It was it, the chip changed from ICM20948 to QMI8658

## ✅ Can't connect the LCD together with the Sense

- Normal Pinout for the LCD, alone works
- Sense Hat (C) alone works.
- Together, the screen shows garbage.

### LCD into SPI(0,1)
This is changing CE0 -> CE1 over SPI0
Does not work

### The DC 25 (physical 22) seem to collide between both
Feels like the Sense and the LEC use the same DC to communicate.

### LCD into SPI(1,0)
Tried as is, fails with
```
FileNotFoundError: [Errno 2] No such file or directory
```

Checked SPI:
```
$ ll /dev/spidev*
crw-rw---- 1 root spi 153, 0 Dec 11 04:49 /dev/spidev0.0
crw-rw---- 1 root spi 153, 1 Dec 11 04:49 /dev/spidev0.1
```

Then followed:
https://tutorials.technology/tutorials/69-Enable-additonal-spi-ports-on-the-raspberrypi.html

- Add a new line into /boot/firmware/config.txt
- reboot

```
$ ll /dev/spidev*
crw-rw---- 1 root spi 153, 0 Dec 11 05:41 /dev/spidev0.0
crw-rw---- 1 root spi 153, 1 Dec 11 05:41 /dev/spidev0.1
crw-rw---- 1 root spi 153, 4 Dec 11 05:41 /dev/spidev1.0
crw-rw---- 1 root spi 153, 3 Dec 11 05:41 /dev/spidev1.1
crw-rw---- 1 root spi 153, 2 Dec 11 05:41 /dev/spidev1.2
```

Now complains about BL being busy. Most likely taken by Sense, but I think that BL on 18 is SPI1CE0 on some Pinouts I've seen.

### Tried to connect the Waveshare Sense HAT (C) through wires

The final fix has been NOT TO CONNECT VIA HAT. Take 4 wires and connect between the HAT holes and the RPi only the I2C pins and power:
- 5v
- GND
- SDA
- SCL

Feels like the Waveshare Sense HAT makes use of all the possible GND to feed the jumpers that it provides to connect extra sensors, but as long as we actually only want the sensors bundled in, and they all work via I2C, we use then what it's only needed.

## RPi does not shutdown as it continues receiving power from UPS. 

WiP

## ✅ Mocking `gpiozero` library with `keyboard` in Mac OS

As I am using the `keyboard` library to mock the button press (alternatives welcome, thanx), on Mac OS M2 halts with 
```
Bus error: 10
```

According to this reported issue:
https://github.com/boppreh/keyboard/issues/619

1. Let it crash,
2. then use `python -X faulthandler` (will open a Python interpreter), appears like the last full stack trace
3. then search for a reference to the file ending with `/keyboard/_darwinkeyboard.py`. Line 134:
```
Carbon.CFDataGetBytes(k_layout, CFRange(0, k_layout_size), ctypes.byref(k_layout_buffer))
```

4. Comment that line
5. Execute the _kleine_ as 'sudo`

### Final solution, switch modules from `keyboard` to `pynput`

https://pypi.org/project/pynput/
