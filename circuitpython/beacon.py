# SPDX-FileCopyrightText: 2021 Uwe Gartmann - digitalwire.ch
#
# SPDX-License-Identifier: MIT

import time
import math
from datadb import DATA_DB

'''
Definitions of movement and heading for beaconing
'''

class SMARTBEACON:

	def __init__(self, size = 10, mode = DATA_DB.buffer_shift):
		self._enabled = False
		self._last_beacon_position = None
		self._last_beacon_heading = None
		self._last_beacon_time = None
		self._heading_log = DATA_DB(size, mode)
		self._heading_deviation_threshold = 2 # percent
		self._beacon_nonmove_rate = 300 # seconds
		self._beacon_hold_time = 15 # seconds
		self._beacon_distance = 1.5 # km
		self._minimum_heading_speed = 2 # km/h
		self._debugging = False

	@property
	def enabled(self):
		return self._enabled

	@enabled.setter
	def enabled(self, v):
		self._enabled = v

	def debugging(self, mode):
		self._debugging = mode

	def update(self, gps):
		send_beacon = False
		if self._enabled == True:
			if gps.is_valid:
				current_position = gps.latitude, gps.longitude
				self._heading_log.add(gps.heading)

				# Check heading deviation / yamartino
				heading_deviation = 0
				if self._last_beacon_position != None:
					if  len(self._heading_log) == self._heading_log.size:
						s=0
						c=0
						n=0.0
						for i in range (0, self._heading_log.size - 1):
							s=s+math.sin(math.radians(self._heading_log.get(i)))
							c=c+math.cos(math.radians(self._heading_log.get(i)))
							n+=1
						s=s/n
						c=c/n
						eps=(1-(s**2+c**2))**0.5
						sigma=math.asin(eps)*(1+(2.0/3.0**0.5-1)*eps**3)
						heading_deviation = math.degrees(sigma)
						# print("heading_deviation", heading_deviation)
						if heading_deviation > self._heading_deviation_threshold:
							if gps.speed_kmh > self._minimum_heading_speed:
								send_beacon = True
				else:
					self._last_beacon_position = current_position
					self._last_beacon_heading = gps.heading
					self._last_beacon_time = time.monotonic()
					send_beacon = True

				# Check if distance is reached
				distance = self._calc_distance(self._last_beacon_position, current_position)
				if distance > self._beacon_distance:
					send_beacon = True

				# Check if non moving timer is reached
				nonmove_timer = self._beacon_nonmove_rate - (time.monotonic() - self._last_beacon_time)
				if nonmove_timer < 0:
					send_beacon = True

				hold_timer = self._beacon_hold_time - (time.monotonic() - self._last_beacon_time)
				if hold_timer > 0:
					send_beacon = False
				
				if self._debugging == True:
					print("BEACON: + > Hold:{0:.0f} Dev:{1:.3f} Dist:{2:.3f} NoMove:{3:.0f}".format(hold_timer, heading_deviation, distance, nonmove_timer))
			else:
				if self._debugging == True:
					print("BEACON: no GPS")
		else:
			if self._debugging == True:
				print("BEACON: off")

		if send_beacon == True:
			self._last_beacon_position = current_position
			self._last_beacon_heading = gps.heading
			self._last_beacon_time = time.monotonic()
			print("BEACON NOW!")

		return send_beacon

	# -----------------------------------------------

	def _calc_distance(self, coord1,coord2):
	    lat1, lon1 = coord1
	    lat2, lon2 = coord2

	    R = 6371000 # radius of Earth in meters
	    phi_1 = math.radians(lat1)
	    phi_2 = math.radians(lat2)

	    delta_phi = math.radians(lat2 - lat1)
	    delta_lambda = math.radians(lon2 - lon1)

	    a = math.sin(delta_phi / 2.0) ** 2 + \
	        math.cos(phi_1) * math.cos(phi_2) * \
	        math.sin(delta_lambda / 2.0) ** 2
	    c = 2 * math.atan2(math.sqrt(a),math.sqrt(1 - a))

	    # meters = R * c # output distance in meters
	    km = R * c / 1000
	    # nauticalmiles = R * c / 1852
	    return km

	def _calc_heading(self, coord1,coord2):
	    lat1, lon1 = coord1
	    lat2, lon2 = coord2

	    R = 6371000 # radius of Earth in meters
	    phi_1 = math.radians(lat1)
	    phi_2 = math.radians(lat2)

	    delta_phi = math.radians(lat2 - lat1)
	    delta_lambda = math.radians(lon2 - lon1)

	    y = math.sin(delta_lambda) * math.cos(phi_2)
	    x = math.cos(phi_1) * math.sin(phi_2) - math.sin(phi_1) * math.cos(phi_2) * math.cos(delta_lambda)
	    heading = (360 + math.degrees(math.atan2(y,x))) % 360
	    return heading

	def _get_coord_from_log(self, log, p):
	    lat = log.get(p).get("lat")
	    lon = log.get(p).get("lon")
	    # print("CoordFromLog:", lat, lon)
	    return float(lat), float(lon)
