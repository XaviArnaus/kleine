from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from definitions import ROOT_DIR

from kleine.lib.utils.ICM20948 import ICM20948


class Main(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

    async def run(self):

        self._xlog.info("🚀 Starting Kleine main run...")

        # --- Your main application logic goes here ---

        import time, math
        print("\nSense HAT Test Program ...\n")
        MotionVal=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        icm20948=ICM20948()
        while True:
            try:
                icm20948.icm20948_Gyro_Accel_Read()
                icm20948.icm20948MagRead()
                MotionVal = icm20948.icm20948CalAvgValue(MotionVal=MotionVal)
                time.sleep(0.1)
                icm20948.imuAHRSupdate(MotionVal[0] * 0.0175, MotionVal[1] * 0.0175,MotionVal[2] * 0.0175,
                            MotionVal[3],MotionVal[4],MotionVal[5], 
                            MotionVal[6], MotionVal[7], MotionVal[8])
                pitch = math.asin(-2 * icm20948.q1 * icm20948.q3 + 2 * icm20948.q0 * icm20948.q2) * 57.3
                roll  = math.atan2(2 * icm20948.q2 * icm20948.q3 + 2 * icm20948.q0 * icm20948.q1, -2 * icm20948.q1 * icm20948.q1 - 2 * icm20948.q2 * icm20948.q2 + 1) * 57.3
                yaw   = math.atan2(-2 * icm20948.q1 * icm20948.q2 - 2 * icm20948.q0 * icm20948.q3, 2 * icm20948.q2 * icm20948.q2 + 2 * icm20948.q3 * icm20948.q3 - 1) * 57.3
                print("\r\n /-------------------------------------------------------------/ \r\n")
                print('\r\n Roll = %.2f , Pitch = %.2f , Yaw = %.2f\r\n'%(roll,pitch,yaw))
                print('\r\nAcceleration:  X = %d , Y = %d , Z = %d\r\n'%(icm20948.Accel[0],icm20948.Accel[1],icm20948.Accel[2]))  
                print('\r\nGyroscope:     X = %d , Y = %d , Z = %d\r\n'%(icm20948.Gyro[0],icm20948.Gyro[1],icm20948.Gyro[2]))
                print('\r\nMagnetic:      X = %d , Y = %d , Z = %d'%((icm20948.Mag[0]),icm20948.Mag[1],icm20948.Mag[2]))
            except(KeyboardInterrupt):
                print("\n")
                break

        # However it happened, just close nicely.
        self.close_nicely()
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely...")
