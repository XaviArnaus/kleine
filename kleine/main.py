from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi
from definitions import ROOT_DIR

from kleine.lib.utils.icm20948_2 import ICM20948


class Main(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(Main, self).init_pyxavi(config=config, params=params)

    def run(self):

        self._xlog.info("🚀 Starting Kleine main run...")

        # --- Your main application logic goes here ---

        import time

        imu = ICM20948(i2c_addr=0x6b, i2c_bus=1)

        try:

            while True:
                x, y, z = imu.read_magnetometer_data()
                ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()

                print(f"""
                    Accel: {ax:05.2f} {ay:05.2f} {az:05.2f}
                    Gyro:  {gx:05.2f} {gy:05.2f} {gz:05.2f}
                    Mag:   {x:05.2f} {y:05.2f} {z:05.2f}""")

                time.sleep(0.25)
        except(KeyboardInterrupt):
            print("\n")

        # However it happened, just close nicely.
        self.close_nicely()
    
    def close_nicely(self):
        self._xlog.debug("Closing nicely...")
