# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

class Values():

    def __init__(self, v):
        self._value = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    def has_changed(self, nv):
        if self._value != nv:
            self._lastvalue = self._value
            self._value = nv
            return True
        else:
            return False

