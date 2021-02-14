# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import os
import board
import digitalio
from aprs import APRS
from tnc import TNC

class DRA818x():

	ptt_off = False
	ptt_on = True

	def __init__(self, uart, mic, ptt_pin, enabled_pin, squelch_pin):
		self._uart = uart
		self._ptt = ptt_pin # Transmit if True (MOSFET Converter installed)
		self._ptt.direction = digitalio.Direction.OUTPUT
		self._enabled = enabled_pin # If True module enabled / Off = Sleep
		self._enabled.direction = digitalio.Direction.OUTPUT
		self._squelch = squelch_pin # If True Squelch = active (no sound)
		self._aprs = APRS()
		self._tnc = TNC(mic)

	@property
	def ptt(self):
		return self._ptt.value

	@ptt.setter
	def ptt(self, v):
		self._ptt.value = v

	@property
	def enabled(self):
		return self._enabled.value

	@enabled.setter
	def enabled(self, v):
		self._enabled.value = v

	def _cmd_send(self,data):
		pass

	def _cmd_response(self):
		pass

	def dmo_set_group(self, gbw, tfv, rfv, tx_ctcss, sq, rx_ctcss):
		pass

	def set_volume(self, level):
		pass

	def set_filter(self, emph, highpass, lowpass):
		pass




