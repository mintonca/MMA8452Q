import smbus
import time
import gpiozero
from ctypes import c_short as short

class MMA8452Q:
    WHO_AM_I = 0x0d
    CTRL_REG1 = 0x2a
    CTRL_REG4 = 0x2d
    def __init__(self, address, bus=1):
        self._addr = address
        self._bus = smbus.SMBus(bus)
    def _read_register(self, reg):
        return self._bus.read_byte_data(self._addr, reg)
    def write_register(self, reg, val):
        return self._bus.write_byte_data(self._addr, reg, val)
    def activate(self):
         c = self._read_register(self.CTRL_REG1)
         self.write_register(self.CTRL_REG1, c | 0x01)
    def standby(self):
         c = self._read_register(self.CTRL_REG1)
         self.write_register(self.CTRL_REG1, c & ~0x01)

    @property
    def XYZ_DATA_CFG(self):
         return self._read_register(0x0e)
    @XYZ_DATA_CFG.setter
    def set_XYZ_DATA_CFG(self, value):
         self.write_register(0x0e, value)

    def set_scale(self, scale):
         cfg = self.XYZ_DATA_CFG
         cfg &= 0xFC
         cfg |= (scale >> 2)
         self.XYZ_DATA_CFG = cfg
         self._scale = scale
         self._scf = float(self._scale)/float(1<<11)

    def set_output_data_rate(self, odr):
         cfg = self._read_register(self.CTRL_REG1)
         cfg &= 0xCF
         cfg |= (odr << 3)
         self.write_register(self.CTRL_REG1, cfg)
    def read(self):
         c = self._bus.read_i2c_block_data(self._addr,0x01,6)
         x = short(c[0]<<8 | c[1]).value>>4
         y = short(c[2]<<8 | c[3]).value>>4
         z = short(c[4]<<8 | c[5]).value>>4
         return tuple(float(_)*self._scf for _ in (x,y,z))
    def enable_drdy_int(self): # for now default to pin INT2
         cfg = self._read_register(self.CTRL_REG4)
         self.write_register(self.CTRL_REG4, cfg | 0x01)

def poll(w):
    while True:
        print w.read()


def print_reading(w):
    x,y,z = w.read()
    f = open("acc_data.log","a")
    f.write("%f\t%f\t%f\t%f\n"%(time.time(),x,y,z))
    f.close()

def foo(): 
    print w.read()

        
w = MMA8452Q(0x1d)
w._read_register(MMA8452Q.WHO_AM_I)
w.standby()
w.set_scale(2)
w.set_output_data_rate(0x04) # 50 Hz
w.enable_drdy_int()
b = gpiozero.Button(18)
#b.when_pressed = foo
b.when_pressed = lambda _:print_reading(w)
w.activate()





