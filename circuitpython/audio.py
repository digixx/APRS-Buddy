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

    def play(self, data, sample_rate = 24000):
        self._dac_waveform = audiocore.RawSample(data, sample_rate = sample_rate)
        self._dac.play(self._dac_waveform, loop = False)
        while self._dac.playing:
            pass
            