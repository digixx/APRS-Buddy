# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import os
import board
import digitalio
import time
import trx_const
from aprs import APRS
from afsk import AFSK

class DRA818x():

	def __init__(self, uart, mic_audio, ptt_pin, enabled_pin, squelch_pin):
		self.off = False
		self.on = True
		self.AFSK = AFSK()
		self.APRS = APRS()
		self._mic_audio = mic_audio

		self._uart = uart
		self._ptt = ptt_pin # Transmit if True (MOSFET Converter installed)
		self._ptt.direction = digitalio.Direction.OUTPUT
		self._ptt.value = self.off

		self._enabled = enabled_pin # If True module enabled / Off = Sleep
		self._enabled.direction = digitalio.Direction.OUTPUT
		self._enabled.value = self.off

		self._squelch_pin = squelch_pin # If True Squelch = active (no sound)
		self._squelch_level = 1 # [0..8]

		self._tx_frequency = '144.800'
		self._rx_frequency = '144.800'

		self._tx_ctcss = 0.0 # means none
		self._rx_ctcss = 0.0 # means none
		self._ctcss_map = trx_const.TONE_MAP

		self._volume = 4
		self._tail_tone = 0

	# --- Hardware -------------------

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
		time.sleep(0.5)

	@property
	def squelch_pin(self):
		return self._squelch_pin.value

	@squelch_pin.setter
	def squelch_pin(self, v):
		self._squelch_pin.value = v

	# --- Values -----------------------

	@property
	def tx_frequency(self):
		return self._tx_frequency

	@tx_frequency.setter
	def tx_frequency(self, v):
		self._tx_frequency = v

	@property
	def rx_frequency(self):
		return self._rx_frequency

	@rx_frequency.setter
	def rx_frequency(self, v):
		self._rx_frequency = v

	@property
	def tx_ctcss(self):
		return self._tx_ctcss

	@tx_ctcss.setter
	def tx_ctcss(self, v):
		self._tx_ctcss = v

	@property
	def rx_ctcss(self):
		return self._rx_ctcss

	@rx_ctcss.setter
	def rx_rtcss(self, v):
		self._rx_ctcss = v

	@property
	def squelch_level(self):
		return self._squelch_level

	@squelch_level.setter
	def squelch_level(self, v):
		self._squelch_level = v

	@property
	def volume(self):
		return self._volume

	@volume.setter
	def volume(self, v):
		self._volume = v
		self._set_volume(self._volume)

	@property
	def tail_tone(self):
		return self._tail_tone

	@tail_tone.setter
	def tail_tone(self, v):
		self._tail_tone = v
		# self._set_tail_tone(self._tail_tone)

	def init(self):
		self._set_group(self._tx_frequency, self._rx_frequency, '0000', self._squelch_level, '0000')
		self._set_filter(0,0,0)

	def send_APRS(self):
		print("Start ARPS Sequence")
		aprs_frame = self.APRS.create_ax25_frame()
		afsk_bit_pattern = self.AFSK.create_afsk_bit_pattern(aprs_frame)

		self.ptt = self.on
		time.sleep(0.5)
		self._mic_audio.play(afsk_bit_pattern)
		self.ptt = self.off

	# --- local functions -----------------

	def _send(self,data):
		self._uart.write(data.encode())
		time.sleep(0.)
		return self._uart.readline()

	def connect(self):
		# check serial connection
		command = 'AT+DMOCONNECT\r\n'
		response = self._send(command)
		if response != None:
			msg = ''.join([chr(b) for b in response])
		print("trx-connect:", msg)

	def _set_group(self, tx_freq, rx_freq, tx_ctcss, sq, rx_ctcss):
		# set most values at once
		command = 'AT+DMOSETGROUP=0,{:.4f},{:.4f},{},{},{}\r\n'.format(tx_freq, rx_freq, tx_ctcss, sq, rx_ctcss)
		print("CMD:", command)
		response = self._send(command)
		if response != None:
			msg = ''.join([chr(b) for b in response])
		print("trx-setgroup:", msg)

	def _set_volume(self, level):
		# set audio out volume [1..8]
		command = 'AT+DMOSETVOLUME={}\r\n'.format(level)
		# print("CMD:", command)
		response = self._send(command)
		if response != None:
			msg = ''.join([chr(b) for b in response])
		print("trx-volume:", msg)

	def _set_tail_tone(self, tone):
		# set tail tone on or off
		command = 'AT+SETTAIL={}\r\n'.format(tone)
		print("CMD:", command)
		response = self._send(command)
		if response != None:
			msg = ''.join([chr(b) for b in response])
		print("trx-tail-tone:", msg)

	def _set_filter(self, emph, highpass, lowpass):
		# This command is used to turn on/off Pre/de-emphasis, Highpass, Lowpass filter
		command = 'AT+SETFILTER={},{},{}\r\n'.format(emph,highpass,lowpass)
		# print("CMD:", command)
		response = self._send(command)
		if response != None:
			msg = ''.join([chr(b) for b in response])
		print("trx-set-filter:", msg)





