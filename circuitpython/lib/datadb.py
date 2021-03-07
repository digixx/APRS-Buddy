# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

class DATA_DB:

    buffer_stop  = const(0x01)
    buffer_shift = const(0x02)

    def __init__(self, size = 10, mode = buffer_shift):
        self._size = size
        if mode == buffer_shift or mode == buffer_stop:
            self._mode = mode
        else:
            raise ValueError
        self._buffer = {}
        self._pointer = 0

    def __len__(self):
        return len(self._buffer)

    def __iter__(self):
        self._pointer = 0
        return self

    def __next__(self):
        l = len(self._buffer)
        if self._pointer < l:
            data = self._buffer[self._pointer]
            self._pointer += 1
            return data
        else:
            raise StopIteration

    @property
    def size(self):
        return self._size

    @property
    def clear(self):
        self._buffer.clear
        self._pointer = 0

    def add(self, data):
        l = len(self._buffer)
        # print("buffer=",l)
        # print("data=", data)

        if self._mode == buffer_stop: # stop when full
            if l < self._size:
                self._buffer[l + 1] = data

        elif self._mode == buffer_shift: # shift data and add new data to the end
            if l < self._size:
                self._buffer[l] = data
            else:
                for x in range(1, l):
                    self._buffer[x - 1] = self._buffer[x]
                self._buffer[l - 1] = data

    def get(self, pos):
        # print("data_db",pos, self._buffer)
        if pos >= 0 and pos < len(self._buffer):
            return self._buffer[pos]
        else:
            raise ValueError

"""
print()
print("**** Start ****")
print()

myLog = data_db(10 , 1)
myLog.add({'date': '29.12.2019', 'time': '13:54:00', 'lat': '47.54467', 'lon': '7.79217'})
myLog.add({'date': '29.12.2019', 'time': '13:55:00', 'lat': '47.54583', 'lon': '7.81733'})
myLog.add({'date': '29.12.2019', 'time': '13:56:00', 'lat': '47.54717', 'lon': '7.84383'})
myLog.add({'date': '29.12.2019', 'time': '13:57:00', 'lat': '47.54683', 'lon': '7.87067'})

print()
print("Logged data:", len(myLog))

for log in myLog:
    lon1 = log.get("lon")
    lat1 = log.get("lat")
    print("Pos= ", lon1,lat1)

print("Log=", myLog.get(1))
"""
