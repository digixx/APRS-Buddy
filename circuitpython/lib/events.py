# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import time

class Events:

    def __init__(self, interval):
        self._interval = interval
        self._time = time.monotonic()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        self._interval = interval

    @property
    def is_due(self):
        ct = time.monotonic()
        if self._time + self._interval < ct:
            self._time = ct
            return True
        else:
            return False


"""
ev1Sec = events(1)
ev5Sec = events(5)


while True:
    if ev1Sec.isdue:
        print('*event* 1')

    if ev5Sec.isdue:
        print('*event* 5')
"""
