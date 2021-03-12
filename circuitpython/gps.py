# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import adafruit_gps_mod

class GPS:

    def __init__(self, uart):
        self._gps = adafruit_gps_mod.GPS(uart, debug = False)
        # Initialize the GPS module by changing what data it sends and at what rate.
        # These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
        # PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
        # the GPS module behavior:
        #   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

        # Set update rate to once a second (1hz) which is what you typically want.
        # gps.send_command(b'PMTK220,1000')
        # Or decrease to once every two seconds by doubling the millisecond value.
        # Be sure to also increase your UART timeout above!
        self._gps.send_command(b'PMTK220,1000') # first command is lost !!
        self._gps.send_command(b'PMTK220,500')

        # Turn on the basic GGA and RMC info (what you typically want)
        self._gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Turn on AIC (Active Interference Cancellation)
        self._gps.send_command(b'PMTK286,1')

        self._debugging = False

    def debugging(self, mode):
        self._debugging = mode

    def info(self):
        if self._debugging == True:
            print("GPS:", end = ' ')
            if self._gps.valid:
                print("Fix", end = " > ")
                print("Lat:", self.latitude_log, end = " ")
                print("Lon:", self.longitude_log, end = " ")
                print("Heading:", self.heading, end = " ")
                print("Alt:", self.altitude_txt)
            else:
                print(" no valid data")

    def update(self):
        self._gps.update()

    @property
    def is_valid(self):
        return self._gps.valid

    @property
    def fix(self):
        return self._gps.fix_quality

    @property
    def fix_3d(self):
        if self._gps.valid:
            return self._gps.fix_quality_3d
        else:
            return 0

    # RAW data - for calculations
    @property
    def latitude(self):
        # 47.51
        return self._gps.latitude

    @property
    def longitude(self):
        # 7.59649
        return self._gps.longitude

    @property
    def speed_knots(self):
        data = 0
        if self._gps.speed_knots is not None:
            data = self._gps.speed_knots
        return data

    @property
    def speed_mph(self):
        data = 0
        if self._gps.speed_mph is not None:
            data = self._gps.speed_mph
        return data

    @property
    def speed_kmh(self):
        data = 0
        if self._gps.speed_kmh is not None:
            data = self._gps.speed_kmh
        return data

    @property
    def heading(self):
        data = 0
        if self._gps.track_angle_deg != None:
            data = self._gps.track_angle_deg
        return data

    @property
    def altitude(self):
        data = 0
        if self._gps.altitude_m is not None:
            data = self._gps.altitude_m
        return data

    '''
    @property
    def time(self):
        data_str = '{:02}:{:02}:{:02}'.format(
        self._gps.timestamp_utc.tm_hour,
        self._gps.timestamp_utc.tm_min,
        self._gps.timestamp_utc.tm_sec)
        return data_str
    '''

    '''
    @property
    def date(self):
        data_str = '{:02}.{:02}.{:04}'.format(
        self._gps.timestamp_utc.tm_mday,
        self._gps.timestamp_utc.tm_mon,
        self._gps.timestamp_utc.tm_year)
        return data_str
    '''

    '''
    @property
    def reverse_date(self):
        data_str = '{:04}_{:02}_{:02}'.format(
        self._gps.timestamp_utc.tm_year,
        self._gps.timestamp_utc.tm_mon,
        self._gps.timestamp_utc.tm_mday)
        return data_str
    '''

    '''
    @property
    def reverse_date_kml(self):
        data_str = '{:04}_{:02}_{:02}_{:02}-{:02}'.format(
        self._gps.timestamp_utc.tm_year,
        self._gps.timestamp_utc.tm_mon,
        self._gps.timestamp_utc.tm_mday,
        self._gps.timestamp_utc.tm_hour,
        self._gps.timestamp_utc.tm_min)
        return data_str
    '''

    '''
    @property
    def satellites_txt(self):
        data_str = "-"
        if self._gps.satellites is not None:
            data_str = '{}'.format(self._gps.satellites)
        return data_str

    @property
    def hdilution_txt(self):
        data_str = "-"
        if self._gps.horizontal_dilution is not None:
            data_str = '{}'.format(self._gps.horizontal_dilution)
        return data_str
    '''

    @property
    def latitude_txt(self):
        Deg = '{:d}'.format(int(self._gps.latitude))
        Min = '{0:.3f}'.format((self._gps.latitude % 1) * 60)
        if self._gps.latitude > 0:
            NS = "N"
        else:
            NS = "S"
        return Deg,Min,NS

    @property
    def longitude_txt(self):
        Deg = '{:d}'.format(int(self._gps.longitude))
        Min = '{0:.3f}'.format((self._gps.longitude % 1) * 60)
        if self._gps.longitude > 0:
            EW = "E"
        else:
            EW = "W"
        return Deg,Min,EW

    @property
    def speed_knots_txt(self):
        data_str = "-"
        if self._gps.speed_knots is not None:
            data_str = '{0:.1f}'.format(self._gps.speed_knots)
        return data_str

    @property
    def speed_mph_txt(self):
        data_str = "-"
        if self._gps.speed_mph is not None:
            data_str = '{0:.1f}'.format(self._gps.speed_mph)
        return data_str

    @property
    def speed_kmh_txt(self):
        data_str = "-"
        if self._gps.speed_kmh is not None:
            data_str = '{0:.1f}'.format(self._gps.speed_kmh)
        return data_str

    @property
    def heading_txt(self):
        data_str = "-"
        if self._gps.track_angle_deg is not None:
            if self._gps.speed_knots > 1:
                data_str = '{0:.0f}'.format(self._gps.track_angle_deg)
        return data_str

    @property
    def altitude_txt(self):
        data_str = "-"
        if self._gps.altitude_m is not None:
            data_str = '{}'.format(self._gps.altitude_m)
        return data_str

    # ---- APRS ----
    def _latitude_aprs(self):
        Deg = '{:02d}'.format(int(self._gps.latitude))
        Min = '{0:.2f}'.format((self._gps.latitude % 1) * 60)
        if self._gps.latitude > 0:
            NS = "N"
        else:
            NS = "S"
        return Deg + Min + NS

    def _longitude_aprs(self):
        Deg = '{:03d}'.format(int(self._gps.longitude))
        Min = '{0:.2f}'.format((self._gps.longitude % 1) * 60)
        if self._gps.longitude > 0:
            EW = "E"
        else:
            EW = "W"
        return Deg + Min + EW

    def _dhm_aprs(self):
        data_str = '{:02}{:02}{:02}z'.format(
        self._gps.timestamp_utc.tm_mday,
        self._gps.timestamp_utc.tm_hour,
        self._gps.timestamp_utc.tm_min)
        return data_str

    def _speed_aprs(self):
        data_str = "000"
        if self._gps.speed_knots is not None:
            data_str = '{:03}'.format(int(round(self._gps.speed_knots)))
        return data_str

    def _heading_aprs(self):
        data_str = "000"
        if self._gps.track_angle_deg is not None:
            if self._gps.speed_knots > 0:
                data_str = '{:03}'.format(int(round(self._gps.track_angle_deg)))
        return data_str

    def _altitude_aprs(self):
        data_str = "000000"
        if self._gps.altitude_m is not None:
            data_str = '{:06}'.format(int(round(self._gps.altitude_m / 0.3048))) # altitude in feet
        return data_str

    @property
    def aprs_position(self):
        return '@{}{}/{}>{}/{}/A={}'.format(self._dhm_aprs(), self._latitude_aprs(), self._longitude_aprs(), self._heading_aprs(), self._speed_aprs(), self._altitude_aprs())

    # ---- LOG ----
    @property
    def latitude_log(self):
        data_str = '{0:.6f}'.format(self._gps.latitude)
        return data_str

    @property
    def longitude_log(self):
        data_str = '{0:.6f}'.format(self._gps.longitude)
        return data_str

"""
ct = time.monotonic()
uart = busio.UART(board.D12, board.D11, baudrate=9600, timeout=20)
myGPS = gps(uart)

while True:
    if ct + 0.5 < time.monotonic():
        ct = time.monotonic()
        myGPS.update()
        print(myGPS.Fix)

"""
