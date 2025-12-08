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