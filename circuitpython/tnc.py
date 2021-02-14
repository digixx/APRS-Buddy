# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
class emulating a modem sending sounds to transceiver
'''
import board
import digitalio
import audiocore
import audioio
from afsk import AFSK

class TNC():
    def __init__(self, DAC, sample_rate = 36000):
        self._DAC = DAC
        self._sample_rate = sample_rate
        self._AFSK = AFSK()

    def send(self, data):
        afsk_bit_pattern = self._AFSK.calc_afsk_bit_pattern(data)
        afsk_dac_waveform = audiocore.RawSample(afsk_bit_pattern, sample_rate = self._sample_rate)
        self._DAC.play(afsk_dac_waveform, loop = False)
        while self._DAC.playing:
            pass








