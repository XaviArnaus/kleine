from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

from IMU import IMU
import math, time


class Accelerometer(PyXavi):
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Accelerometer, self).init_pyxavi(config=config, params=params)
    
    def test(self):

        self._xlog.info("🚀 Starting Accelerometer test run...")

        print("\nSense HAT Test Program ...\n")
        MotionVal=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        imu=IMU()
        while True:
            try:
                imu.QMI8658_Gyro_Accel_Read()
                imu.AK09918_MagRead()
                MotionVal = imu.icm20948CalAvgValue(MotionVal=MotionVal)
                imu.imuAHRSupdate(MotionVal[0] * 0.0175, MotionVal[1] * 0.0175,MotionVal[2] * 0.0175,
                            MotionVal[3],MotionVal[4],MotionVal[5], 
                            MotionVal[6], MotionVal[7], MotionVal[8])
                pitch = math.asin(-2 * imu.q1 * imu.q3 + 2 * imu.q0 * imu.q2) * 57.3
                roll  = math.atan2(2 * imu.q2 * imu.q3 + 2 * imu.q0 * imu.q1, -2 * imu.q1 * imu.q1 - 2 * imu.q2 * imu.q2 + 1) * 57.3
                yaw   = math.atan2(-2 * imu.q1 * imu.q2 - 2 * imu.q0 * imu.q3, 2 * imu.q2 * imu.q2 + 2 * imu.q3 * imu.q3 - 1) * 57.3
                print("\r\n /-------------------------------------------------------------/ \r\n")
                print('\r\n Roll = %.2f , Pitch = %.2f , Yaw = %.2f\r\n'%(roll,pitch,yaw))
                print('\r\nAcceleration:  X = %d , Y = %d , Z = %d\r\n'%(imu.Accel[0],imu.Accel[1],imu.Accel[2]))  
                print('\r\nGyroscope:     X = %d , Y = %d , Z = %d\r\n'%(imu.Gyro[0],imu.Gyro[1],imu.Gyro[2]))
                print('\r\nMagnetic:      X = %d , Y = %d , Z = %d\r\n'%((imu.Mag[0]),imu.Mag[1],imu.Mag[2]))
                print("QMITemp=%.2f C\r\n"%imu.QMI8658_readTemp())
                time.sleep(0.1)
            except(KeyboardInterrupt):
                print("\n")
                break
    
