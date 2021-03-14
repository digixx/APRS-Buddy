# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import gc
print("MAIN: Mem start", gc.mem_free())

import board
import time
import events
import m_io
from beacon import SMARTBEACON

# Declare Events
ev1sec = events.Events(1)
ev10sec = events.Events(10)

# GPS Module
GPS = m_io.init_gps()
GPS.debugging = False

# Sensors
ENV = m_io.init_environment()
ENV.debugging = False
ACC = m_io.init_acc()
ACC.debugging = False

# SD Card
SDC = m_io.init_sdcard()
if SDC.available():
	SDC.create_dir('/logs')
	SDC.create_dir('/kml')
	SDC.list_dir()
	SDC.list_dir('/logs')
	SDC.list_dir('/kml')
	print("SD-Card free space:", SDC.get_free_space(), "MB")
	print('\n')
else:
	print('no SD-Card found\n')

# BEACON / detect fast direction changes
BEACON = SMARTBEACON()
BEACON.debugging = True
BEACON.enabled = True
BEACON.nonmove_rate = 1200 # seconds
BEACON.hold_time = 15 # seconds
BEACON.min_distance = 1.5 # km
BEACON.min_heading_speed = 2 # km/h
BEACON.heading_deviation_threshold = 2 # percent

# TRX
TRX = m_io.init_trx()
TRX.debugging = True
TRX.init()
TRX.APRS.source = "HB9FZG-4"
TRX.APRS.digipeaters = 'WIDE1-1,WIDE2-1'

# Voltmeter
VMTR = m_io.init_voltmeter()
VMTR.debugging = True

while True:
	GPS.update()

	if ev1sec.is_due:
		if BEACON.update(GPS) == True:
			TRX.APRS.information = GPS.aprs_position + " Batt:{:.1f}V".format(VMTR.voltage)
			TRX.send_APRS()

	if ev10sec.is_due:
		ENV.info()
		ACC.info()
		VMTR.info()
		GPS.info()
		