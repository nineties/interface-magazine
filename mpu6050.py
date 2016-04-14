# -*- coding: utf-8 -*-

import ctypes
from smbus import SMBus

class MPU6050(object):
    def __init__(self, bus_id=1, base=0x68, normalize=False):
        self.bus = SMBus(bus_id)
        self.base = base

        # Wake the chip up.
        self.bus.write_byte_data(self.base, 0x6b, 0)

        # Gyroscope configuration
        assert(self.bus.read_byte_data(self.base, 0x1b) == 0)
        self.gyro_scale = 131.0
        if normalize:
            self.gyro_scale *= 250

        # Accelerometer configuration
        assert(self.bus.read_byte_data(self.base, 0x1c) == 0)
        self.accel_scale = 16384.0
        if normalize:
            self.accel_scale *= 2

    def _read_word(self, addr):
        high = self.bus.read_byte_data(self.base, addr)
        low = self.bus.read_byte_data(self.base, addr+1)
        return ctypes.c_short((high << 8) + low).value

    def get(self):
        accel_xout = self._read_word(0x3b)/self.accel_scale
        accel_yout = self._read_word(0x3d)/self.accel_scale
        accel_zout = self._read_word(0x3f)/self.accel_scale
        gyro_xout = self._read_word(0x43)/self.gyro_scale
        gyro_yout = self._read_word(0x45)/self.gyro_scale
        gyro_zout = self._read_word(0x47)/self.gyro_scale
        return [
                accel_xout, accel_yout, accel_zout,
                gyro_xout, gyro_yout, gyro_zout
                ]
