# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import os
import board
import busio
import digitalio

import neopixel
from sdcard import SD_Card
from sensors import BMP280
from sensors import LIS3DH
from audio import AUDIO
from gps import GPS
from trx import DRA818x
from voltmeter import VOLTMETER

NEOpix = neopixel.NeoPixel(board.NEOPIXEL, 1)
NEOpix[0] = (0, 0, 0) # set off

InfoLED1 = digitalio.DigitalInOut(board.D10)
InfoLED1.direction = digitalio.Direction.OUTPUT
InfoLED2 = digitalio.DigitalInOut(board.D11)
InfoLED2.direction = digitalio.Direction.OUTPUT

InfoLED1.value = False
InfoLED2.value = False

# Create the SPI bus for multiple devices
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

def init_environment():
    bmp_cs = digitalio.DigitalInOut(board.D6)
    bmp_sensor = BMP280(spi, bmp_cs)
    bmp_sensor.sea_level_pressure = 1013
    return bmp_sensor

def init_acc():
    acc_cs = digitalio.DigitalInOut(board.D9)
    acc_sensor = LIS3DH(spi, acc_cs)
    acc_sensor.range = LIS3DH.RANGE_2_G
    return acc_sensor

def init_sdcard():
    sd_cs = digitalio.DigitalInOut(board.D5)
    # sd_cd = digitalio.DigitalInOut(board.A5)
    sd_root = '/sd'
    sdc = SD_Card(spi, sd_cs, None, sd_root)
    return sdc

def init_gps():
    gps_uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=20, receiver_buffer_size=256)
    gps = GPS(gps_uart)
    return gps

def init_trx():
    # create serial channel
    trx_uart = busio.UART(board.SDA, board.SCL, baudrate=9600, timeout=2, receiver_buffer_size=32)
    # create audio channel playing wave data
    trx_microphon = AUDIO(board.A0)
    # set digital output for power savings
    trx_enabled = digitalio.DigitalInOut(board.D4)
    # set digital input for detecting rf reception
    trx_squelch = digitalio.DigitalInOut(board.D12)
    # set PTT
    trx_ptt = digitalio.DigitalInOut(board.D13)
    # Init TRX
    trx = DRA818x(trx_uart, trx_microphon, trx_ptt, trx_enabled, trx_squelch)
    return trx

def init_voltmeter():
    vmtr = VOLTMETER(board.A3, span=3.3, divider=11)
    return vmtr

