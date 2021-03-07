# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import sys
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
GPS.debugging(True)

# Sensors
ENV = m_io.init_environment()
ENV.debugging(True)

ACC = m_io.init_acc()
ACC.debugging(True)

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
BEACON.debugging(True)
BEACON.enabled = True


# TRX
TRX = m_io.init_trx()
TRX.debugging(True)
TRX.enabled = 1

TRX.tx_frequency = 144.800
TRX.rx_frequency = 144.800
TRX.squelch_level = 1
TRX.init()
TRX.volume = 2
TRX.tail_tone = 0

TRX.APRS.debug = False
TRX.APRS.source = 'HB9FZG-4'

# Voltmeter
VMTR = m_io.init_voltmeter()
VMTR.debugging(True)

loops = 0

while True:
	tstart = time.monotonic()
	GPS.update()
	tstop = time.monotonic()

	if tstop - tstart > 0.5:
		print("MAIN: Update overload")

	if ev1sec.is_due:
		# Environment
		# print("Temp / Pressure:", ENV.temp, ENV.pressure)
		if gps_fix_status.has_changed(GPS.fix > 0):
			print("GPS: Fix changed:", GPS.fix)

		# ACC Sensor
		x, y, z = [value / ACC.standard_gravity for value in ACC.acceleration]
		# print("ACC: x = %0.3fG, y = %0.3fG, z = %0.3fG" % (x, y, z))

		# GPS
		if GPS.is_valid:
			pass

		
		# show power
		# print("Voltage: {:.2f}".format(VMTR.voltage))

		BEACON.update(GPS)

	if ev5sec.is_due:
		if GPS.is_valid:
			TRX.APRS.information = GPS.aprs_position + " Batt:{:.1f}V".format(VMTR.voltage)
			# TRX.dmo_connect()
			# print("APRS-MSG:", TRX.APRS.information)
			if loops > 0:
				TRX.send_APRS()
				loops =- 1
			# sys.exit()
			# pass

	if ev10sec.is_due:
		ENV.info()
		ACC.info()
		VMTR.info()
		GPS.info()
	