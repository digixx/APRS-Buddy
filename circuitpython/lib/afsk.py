# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
Class for transforming APRS data into audio-byte-array using NRZI encoding
'''
import math
import array

class AFSK():
    debugging = False
    AX25_FLAG = 0x7e    # AX.25 Flag (Frame Deliminator, not affected from bit stuffing)

    _mark = 0
    _space = 1
    _start_frequency = _mark

    _DAC_range = 100
    _DAC_idle_level = 127

    def __init__(self, bps_rate = 1200, frequency_space = 2200, frequency_mark = 1200, _datapoints_per_bit = 30):
        self._bps_rate = bps_rate
        self._datapoints_per_bit = _datapoints_per_bit
        self._sample_rate = self._bps_rate * self._datapoints_per_bit
        self._frequency_space = frequency_space
        self._frequency_mark = frequency_mark
        self._phase = 0
        self._preamble_head_length = 20
        self._preamble_tail_length = 5

        self._datapoints_per_bit = self._sample_rate / self._bps_rate
        self._space_degree_incr = int(360 * self._frequency_space / self._bps_rate / self._datapoints_per_bit)
        self._mark_degree_incr = int(360 * self._frequency_mark / self._bps_rate / self._datapoints_per_bit)

        # calculate static sinus table for every degree
        self._sinus_table = []
        for degree in range(0,360):
            sinus_value = (math.sin(math.pi * 2 * degree / 360))
            sinus_table_dac_value = round(sinus_value * (self._DAC_range / 2) + self._DAC_idle_level)
            self._sinus_table.append(sinus_table_dac_value)
        self._init_sequence()

    @property
    def samplerate(self):
        return self._sample_rate

    def _init_sequence(self):
        self._tone = self._start_frequency
        self._bit_stuff_cntr = 0
        self._phase = 0
        self._sequence =  array.array('B',[])

    def _add_tone_to_sequence(self):
        if self._tone == self._space:
            phase_incr = self._space_degree_incr
        else:
            phase_incr = self._mark_degree_incr

        for dp in range(0, self._datapoints_per_bit):
            self._phase = (self._phase + phase_incr) % 360
            self._sequence.append(self._sinus_table[self._phase])

        self._bit_stuff_cntr += 1

    def _swap_tone(self):
        if self._tone == self._space:
            self._tone = self._mark
        else:
            self._tone = self._space
        self._bit_stuff_cntr = 0

    def _add_data_byte(self, b):
        for x in range(0, 8):
            if b & (1 << x) == 0:
                self._swap_tone()
            self._add_tone_to_sequence()

            if self._bit_stuff_cntr > 5:
                self._swap_tone()
                self._add_tone_to_sequence()

    def _add_preamble(self, length):
        for x in range(length):
            for x in range(0, 8):
                if self.AX25_FLAG & (1 << x) == 0:
                    self._swap_tone()
                self._add_tone_to_sequence()
            self._bit_stuff_cntr = 0

    def _prime_dac_level(self, value):
        for x in range(0,50):
            self._sequence.append(self._sinus_table[0])

    def calc_afsk_bit_pattern(self, data):
        self._init_sequence()
        self._prime_dac_level(20)
        self._add_preamble(self._preamble_head_length)
        for x in range(len(data)):
            self._add_data_byte(data[x])
        self._add_preamble(self._preamble_tail_length)
        self._prime_dac_level(20)
        return self._sequence