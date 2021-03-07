# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import adafruit_bmp280
import adafruit_lis3dh

class BMP280:

    def __init__(self, spi, bmp_cs):
        self._bmp = adafruit_bmp280.Adafruit_BMP280_SPI(spi, bmp_cs)
        self._bmp.sea_level_pressure = 1013
        self._debugging = False

    @property
    def sea_level_pressure(self):
        return self._bmp.sea_level_pressure

    @sea_level_pressure.setter
    def sea_level_pressure(self, value):
        self._bmp.sea_level_pressure = value

    @property
    def temp(self):
        return '%0.1f' % self._bmp.temperature

    @property
    def pressure(self):
        return '%0.1f' % self._bmp.pressure

    @property
    def pressure_hi_res(self):
        return self._bmp.pressure

    @property
    def temp_hi_res(self):
        return self._bmp.temperature

    def debugging(self, mode):
        self._debugging = mode        

    def info(self):
        if self._debugging == True:
            print("BMP:", end = " ")
            print("Temp: ", self.temp, end = " ")
            print("Press: ", self.pressure)

class LIS3DH:

    STANDARD_GRAVITY = 9.806
    RANGE_16_G = const(0b11)  # +/- 16g
    RANGE_8_G = const(0b10)  # +/- 8g
    RANGE_4_G = const(0b01)  # +/- 4g
    RANGE_2_G = const(0b00)  # +/- 2g (default value)

    def __init__(self, spi, acc_cs):
        self._acc = adafruit_lis3dh.LIS3DH_SPI(spi, acc_cs)
        self._debugging = False

    @property
    def standard_gravity(self):
        return self.STANDARD_GRAVITY

    @property
    def acceleration(self):
        return self._acc.acceleration

    def debugging(self, mode):
        self._debugging = mode

    def info(self):
        if self._debugging == True:
            x, y, z = [value / self.standard_gravity for value in self.acceleration]
            print("ACC: x= %0.3fG, y= %0.3fG, z= %0.3fG" % (x, y, z))

"""
ct = time.monotonic()

# Create the SPI bus
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
bmp_cs = digitalio.DigitalInOut(board.D5)
sensor = BMP280(spi, bmp_cs)
sensor.sea_level_pressure = 1013

while True:
    if ct + 0.5 < time.monotonic():
        ct = time.monotonic()
        print('Temp=', sensor.Temp)
        print('Press=', sensor.Pressure)
"""
