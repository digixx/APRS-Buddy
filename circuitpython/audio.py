# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
Class handling audio
'''

import board
import audiocore
import audioio

class AUDIO():
    def __init__(self, DAC):
        self._dac = audioio.AudioOut(DAC)
        self._sample_rate = 36000

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = value

    def play(self, data):
        self._dac_waveform = audiocore.RawSample(data, sample_rate = self._sample_rate)
        self._dac.play(self._dac_waveform, loop = False)
        while self._dac.playing:
            pass









