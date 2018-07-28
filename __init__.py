import smbus
import time
#import gpiozero
from ctypes import c_short as short

class MMA8452Q(object):
    def __init__(self, address, bus=1):
        self._addr = address
        self._bus = smbus.SMBus(bus)
	if self.WHO_AM_I != 0x2a:
	    raise ValueError("Unexpected WHO_AM_I result.")
    def _read_register(self, reg):
        return self._bus.read_byte_data(self._addr, reg)
    def write_register(self, reg, val):
        return self._bus.write_byte_data(self._addr, reg, val)

    def __register__(reg_add, ro=False):
         def getter(self): 
             return self._read_register(reg_add)
         if ro:
         	return property(getter)
         def setter(self, val): 
             return self.write_register(reg_add, val)
         return property(getter, setter)

    WHO_AM_I = __register__(0x0d, True)
    XYZ_DATA_CFG = __register__(0x0e)
    CTRL_REG1 = __register__(0x2a)
    CTRL_REG4 = __register__(0x2d)
    CTRL_REG5 = __register__(0x2e)

    def activate(self):
         self.CTRL_REG1 |= 1
    def standby(self):
         self.CTRL_REG1 &= ~0x01

    def set_scale(self, scale):
         cfg = self.XYZ_DATA_CFG
         cfg &= 0xFC
         cfg |= (scale >> 2)
         self.XYZ_DATA_CFG = cfg
         self._scale = scale
         self._scf = float(self._scale)/float(1<<11)

    def set_output_data_rate(self, odr):
         cfg = self.CTRL_REG1
         cfg &= 0xCF
         cfg |= (odr << 3)
         self.CTRL_REG1 = cfg

    @property
    def data(self):
         c = self._bus.read_i2c_block_data(self._addr,0x01,6)
         x = short(c[0]<<8 | c[1]).value>>4
         y = short(c[2]<<8 | c[3]).value>>4
         z = short(c[4]<<8 | c[5]).value>>4
         return tuple(float(_)*self._scf for _ in (x,y,z))

    def __interrupt__(bit):
         mask = 1<<bit
         def getter(self):
             if self.CTRL_REG4 & mask: # interrupt enabled, return 1 or 2 for the line
                 if self.CTRL_REG5 & mask: 
		     return 1
		 else: 
		     return 2
             else:
                 return 0
         def setter(self, val):
	     if val == 0:
	         self.CTRL_REG4 &= ~mask
             else:
	         self.CTRL_REG4 |= mask 
		 self.CTRL_REG5 &= ~mask
		 if val == 1:
		    self.CTRL_REG5 |= mask
         return property(getter, setter)

    INT_DRDY = __interrupt__(0)

    def enable_drdy_int(self): # for now default to pin INT2
         cfg = self.CTRL_REG4
         self.CTRL_REG4 = cfg | 0x01

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

        
#w = MMA8452Q(0x1d)
#w.standby()
#w.set_scale(2)
#w.set_output_data_rate(0x04) # 50 Hz
#w.enable_drdy_int()
#b = gpiozero.Button(18)
##b.when_pressed = foo
#b.when_pressed = lambda _:print_reading(w)
#w.activate()





