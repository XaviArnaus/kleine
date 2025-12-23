from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class MockedIMU(PyXavi):

    Gyro  = [0,0,0]
    Accel = [0,0,0]
    Mag   = [0,0,0]
    pitch = 0.0
    roll  = 0.0
    yaw   = 0.0
    pu8data=[0,0,0,0,0,0,0,0]
    U8tempX=[0,0,0,0,0,0,0,0,0]
    U8tempY=[0,0,0,0,0,0,0,0,0]
    U8tempZ=[0,0,0,0,0,0,0,0,0]
    GyroOffset=[0,0,0]
    Ki = 1.0
    Kp = 4.50
    q0 = 1.0
    q1=q2=q3=0.0
    angles=[0.0,0.0,0.0]
    
    def __init__(self, config: Config = None, params: Dictionary = None):
        super(MockedIMU, self).init_pyxavi(config=config, params=params)

    def QMI8658_Gyro_Accel_Read(self):
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    
    def AK09918_MagRead(self):
        return (0.0, 0.0, 0.0)
    
    def icm20948CalAvgValue(self, MotionVal):
        return [0.0]*9
    
    def imuAHRSupdate(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        pass

    def QMI8658_readTemp(self):
        return 25.0