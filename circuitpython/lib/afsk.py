# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

'''
Class for transforming APRS data into audio-byte-array using NRZI encoding
'''
import math
import array
import gc


class AFSK():

    AX25_FLAG = 0x7e    # AX.25 Flag (Frame Deliminator, not affected from bit stuffing)
    _mark = 0
    _space = 1
    _start_frequency = _space # we start with space because the radios audio levels faster

    _DAC_preemphasis_mark = 0.4
    _DAC_preemphasis_space = 1
    _DAC_amplitude = 125
    _DAC_idle_level = 127

    def __init__(self, bps_rate = 1200, frequency_space = 2200, frequency_mark = 1200, _datapoints_per_bit = 15):
        self._datapoints_per_bit = _datapoints_per_bit
        self._sample_rate = bps_rate * self._datapoints_per_bit
        self._phase = 0
        self._preamble_head_length = 30
        self._preamble_tail_length = 10

        self._datapoints_per_bit = self._sample_rate / bps_rate
        self._space_degree_incr = int(360 *frequency_space / bps_rate / self._datapoints_per_bit)
        self._mark_degree_incr = int(360 * frequency_mark / bps_rate / self._datapoints_per_bit)
        self._debugging = False

        # print("AFSK: before table", gc.mem_free())
        self._sinus_table = []
        for degree in range(0,360):
            sinus_value = (math.sin(math.pi * 2 * degree / 360))
            sinus_table_dac_value = int(sinus_value * self._DAC_amplitude)
            self._sinus_table.append(sinus_table_dac_value)
            # print(degree, sinus_table_dac_value, int(sinus_table_dac_value * self._DAC_preemphasis_space) + self._DAC_idle_level, int(sinus_table_dac_value * self._DAC_preemphasis_mark) + self._DAC_idle_level)
        self._init_sequence()
        # print("AFSK: after table", gc.mem_free())

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
            for dp in range(0, self._datapoints_per_bit):
                self._phase = (self._phase + self._space_degree_incr) % 360
                DAC_value = int(self._sinus_table[self._phase] * self._DAC_preemphasis_space) + self._DAC_idle_level
                self._sequence.append(DAC_value)
        else:
            for dp in range(0, self._datapoints_per_bit):
                self._phase = (self._phase + self._mark_degree_incr) % 360
                DAC_value = int(self._sinus_table[self._phase] * self._DAC_preemphasis_mark) + self._DAC_idle_level
                self._sequence.append(DAC_value)

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
        for l in range(length):
            for x in range(0, 8):
                if self.AX25_FLAG & (1 << x) == 0:
                    self._swap_tone()
                self._add_tone_to_sequence()
            self._bit_stuff_cntr = 0

    def _prime_dac_level(self):
        for x in range(0,30):
            self._sequence.append(self._DAC_idle_level)

    def create_afsk_bit_pattern(self, data):
        self._init_sequence()
        self._prime_dac_level()
        self._add_preamble(self._preamble_head_length)
        for x in range(len(data)):
            self._add_data_byte(data[x])
        self._add_preamble(self._preamble_tail_length)
        self._prime_dac_level()
        return self._sequence

