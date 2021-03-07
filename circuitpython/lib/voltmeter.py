# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import board
import analogio

class VOLTMETER:

	def __init__(self, ADC, span = 3.3, divider = 11):
		self._adc = analogio.AnalogIn(ADC)
		self._span = span
		self._resolution = 65536
		self._divider = divider
		self._debugging = False

	@property
	def voltage(self):
		return self._span / self._resolution * self._adc.value * self._divider

	def debugging(self, mode):
		self._debugging = mode        

	def info(self):
		if self._debugging == True:
			print("VMTR:", end = " ")
			print("Batt: ", self.voltage)
