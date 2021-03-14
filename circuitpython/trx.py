# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import os
import board
import digitalio
import time
from aprs import APRS
from afsk import AFSK

class DRA818x():

	def __init__(self, uart, mic_audio, ptt_pin, enabled_pin, squelch_pin):
		self.debugging = False
		self.AFSK = AFSK()
		self.APRS = APRS()

		self.tx_frequency = 144.800
		self.rx_frequency = 144.800
		self.squelch_level = 1 # [0..8]

		self._mic_audio = mic_audio
		self._uart = uart

		self._ptt = ptt_pin # Transmit if True (MOSFET Converter installed)
		self._ptt.direction = digitalio.Direction.OUTPUT
		self._ptt.value = False

		self._enabled = enabled_pin # If True module enabled / Off = Sleep
		self._enabled.direction = digitalio.Direction.OUTPUT
		self._enabled.value = False

		self._squelch_pin = squelch_pin # If True Squelch = active (no sound)



		self._volume = 2
		self._enable_ptt = True # set it to false to avoid sending real HF

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

	'''
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
	def squelch_level(self):
		return self._squelch_level

	@squelch_level.setter
	def squelch_level(self, v):
		self._squelch_level = v
	'''

	@property
	def volume(self):
		return self._volume

	@volume.setter
	def volume(self, v):
		self._volume = v
		self._set_volume(self._volume)

	def connect(self):
		# check serial connection
		if self._debugging == True:
			print("TRX: connect", end = ": ")
		command = 'AT+DMOCONNECT\r\n'
		response = self._send(command)

	def init(self):
		self.enabled = True
		time.sleep(0.5)
		self._set_group(self.tx_frequency, self.rx_frequency, '0000', self.squelch_level, '0000')
		self._set_filter(0,0,0)
		self.enabled = False

	def send_APRS(self):
		aprs_frame = self.APRS.create_ax25_frame()
		aprs_frame = self.AFSK.create_afsk_bit_pattern(aprs_frame)

		## sending APRS to Air
		if self._enable_ptt == True:
			self.enabled = True
			time.sleep(2)
			self.ptt = True
			time.sleep(1.5)
			self._mic_audio.play(aprs_frame, self.AFSK.samplerate)
			self.enabled = False
			self.ptt = False
			
		else:
			print("TRX: -ptt +sound")
			self._mic_audio.play(aprs_frame)

	# --- local functions -----------------

	def _send(self,data):
		if self._enabled.value == True:
			self._uart.write(data.encode())
			response =  self._uart.readline()
			if response != None:
				response = ''.join([chr(b) for b in response])
			else:
				response = "n/a"
		return response

	def _set_group(self, tx_freq, rx_freq, tx_ctcss, sq, rx_ctcss):
		# set most values at once
		command = 'AT+DMOSETGROUP=0,{:.4f},{:.4f},{},{},{}\r\n'.format(tx_freq, rx_freq, tx_ctcss, sq, rx_ctcss)
		response = self._send(command)
		if self.debugging == True:
			print("TRX: set group: ", response)

	def _set_volume(self, level):
		# set audio out volume [1..8]
		command = 'AT+DMOSETVOLUME={}\r\n'.format(level)
		response = self._send(command)
		if self.debugging == True:
			print("TRX: set volume: ", response)

	def _set_filter(self, emph, highpass, lowpass):
		# This command is used to turn on/off Pre/de-emphasis, Highpass, Lowpass filter
		command = 'AT+SETFILTER={},{},{}\r\n'.format(emph,highpass,lowpass)
		response = self._send(command)
		if self.debugging == True:
			print("TRX: set filter: ", response)
