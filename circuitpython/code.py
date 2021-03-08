# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

# import sys
import gc

print("MAIN: First Memory", gc.mem_free())

import board
import time
import events
import vars
import m_io
from beacon import SMARTBEACON

# Declare Events
ev1sec = events.Events(1)
ev5sec = events.Events(5)
ev10sec = events.Events(10)

# Global vars
gps_fix_status = vars.Values("0")

# GPS Module
GPS = m_io.init_gps()
GPS.debugging(False)

# Sensors
ENV = m_io.init_environment()
ENV.debugging(False)

ACC = m_io.init_acc()
ACC.debugging(False)

'''
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
'''

BEACON = SMARTBEACON()
BEACON.debugging(False)
BEACON.enabled = True

# TRX
TRX = m_io.init_trx()
TRX.debugging(True)
TRX.enabled = 0
TRX.tx_frequency = 144.800
TRX.rx_frequency = 144.800
TRX.squelch_level = 1
TRX.init()
TRX.volume = 2
TRX.APRS.source = 'HB9FZG-4'

# Voltmeter
VMTR = m_io.init_voltmeter()
VMTR.debugging(False)

while True:
	tstart = time.monotonic()
	GPS.update()

	tstop = time.monotonic()

	if tstop - tstart > 0.5:
		print("MAIN: Update overload")

	if ev1sec.is_due:
		if gps_fix_status.has_changed(GPS.fix > 0):
			print("GPS: Fix changed:", GPS.fix)

		if BEACON.update(GPS) == True:
			gc.collect()
			TRX.APRS.information = GPS.aprs_position + " Batt:{:.1f}V".format(VMTR.voltage)
			TRX.send_APRS()

	if ev5sec.is_due:
		if GPS.is_valid:
			# TRX.APRS.information = GPS.aprs_position + " Batt:{:.1f}V".format(VMTR.voltage)
			# TRX.dmo_connect()

			# sys.exit()
			pass

	if ev10sec.is_due:
		ENV.info()
		ACC.info()
		VMTR.info()
		GPS.info()
