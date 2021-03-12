# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import os
import storage
import adafruit_sdcard

class SD_Card:

    def __init__(self, spi, sd_cs, sd_cd = None, root = '/sd'):
        self._sdc = adafruit_sdcard.SDCard(spi, sd_cs)
        self._cd = sd_cd
        self._vfs = storage.VfsFat(self._sdc)
        self._root = root
        storage.mount(self._vfs, self._root)

    def available(self):
        return self._sdc.available()

    def get_free_space(self):
        fsp = os.statvfs(self._root)
        f_bsize = float(fsp[0])
        f_bavail = float(fsp[4])
        return (f_bsize * f_bavail) / 1048576

    def write_to_file(self, directory, filename, data):
        target = self._root + directory + filename
        try:
            with open(target, "w") as f:
                f.write(data)
        except:
            pass

    def append_to_file(self, directory, filename, data):
        target = self._root + directory + filename
        try:
            with open(target, "a") as f:
                f.write(data)
        except:
            pass

    def create_dir(self, directory):
        try:
            os.mkdir(self._root + directory)
        except OSError as exc:
            if exc.args[0] == 17: # errno.EEXIST:
                print('OSInfo: dir exists:', directory)
                pass
            else:
                raise exc

    def delete_file(self, directory, filename):
        target = self._root + directory + filename
        try:
            os.remove(target)
        except:
            pass

    def list_dir(self, path = ''):
        for file in os.listdir(self._root + path):
            try:
                stats = os.stat(self._root + path + "/" + file)
                filesize = stats[6]
                isdir = stats[0] & 0x4000

                if filesize < 1000:
                    sizestr = str(filesize) + " Byte"
                elif filesize < 1000000:
                    sizestr = "%0.1f KB" % (filesize / 1000)
                else:
                    sizestr = "%0.1f MB" % (filesize / 1000000)

                if path == '':
                    prettyprintname = file
                else:
                    prettyprintname = path + '/' + file

                if isdir:
                    prettyprintname += "/"

                print('{0:<20} Size: {1:>10}'.format(prettyprintname, sizestr))

            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    print("OSError, FileNotFound:" + self._root + "/" + file)
                else:
                    raise exc

    def write_to_log(self, revdate, date, time, lat, lon, speed):
        data_str = '{} {} {} {} {}'.format(date, time, lat, lon, speed)
        print("SDC:", data_str)
        self.append_to_file("/logs/", revdate, data_str + '\n')

    def create_kml_file(self, filename, name):
        target = self._root + "/kml/" + filename + ".kml"
        try:
            with open(target, "a") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')
                f.write('<Document>\n')
                f.write('\t<name>KML_' + filename + '</name>\n')
                f.write('\t<Style><PolyStyle><fill>0</fill><outline>1</outline></PolyStyle></Style>\n')
                f.write('\t<Placemark>\n')
                f.write('\t\t<name>' + name + '</name>\n')
                f.write('\t\t<LineString><coordinates>\n\t\t\t')
                print("createKMLfile:", target)
        except:
            pass

    def add_kml_data(self, filename, lat, lon, asl):
        target = self._root + "/kml/" + filename  + ".kml"
        try:
            with open(target, "a") as f:
                data_str = '{},{},{} '.format(lon, lat, asl)
                f.write(data_str)
                print("addKMLdata:", data_str)
        except:
            print("addKMLdata: Error")

    def close_kml_file(self, filename):
        target = self._root + "/kml/" + filename + ".kml"
        try:
            with open(target, "a") as f:
                f.write('\n\t\t</coordinates></LineString>\n')
                f.write('\t</Placemark>\n')
                f.write('</Document>\n')
                f.write('</kml>\n')
                print("closeKMLfile:", target)
        except:
            pass

    def read_file(self, directory, filename):
        target = self._root + directory + filename
        with open(target, "r") as f:
            line = f.readline()
            while line != '':
                print(line)
                line = f.readline()

"""
ct = time.monotonic()
# Create the SPI bus
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# Create the SPI bus
sd_cs = digitalio.DigitalInOut(board.D9)
sd_cd = digitalio.DigitalInOut(board.D6)
sdc = sdcard(spi, sd_cs, sd_cd)

if sdc.available():
    sdc.print_directory('/sd')
else:
    print('no Card found')

while True:
    if ct + 0.5 < time.monotonic():
        ct = time.monotonic()

"""
