from math import sin, cos, sqrt, atan2, radians
import os
import sqlite3

db_path = os.path.dirname(__file__) + "/china_city_geo.db"

# Get radian distance between two coordinates.
def latlon2distance(latitude1, longitude1, latitude2, longitude2):
	lat1, lon1, lat2, lon2 = radians(latitude1), radians(longitude1), radians(latitude2), radians(longitude2)
	a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
	return 2 * atan2(sqrt(a), sqrt(1 - a))

# Geo hash from given coordinates.
def latlon2geohash(latitude, longitude, precision = 12):
	BASE_32 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "b", "c", "d", "e", "f", "g", "h", "j", "k", "m", "n", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
	BITS = [16, 8, 4, 2, 1]
	latInterval, lngInterval = [-90.0, 90.0], [-180.0, 180.0]
	geohash = ""
	isEven, bit, ch = True, 0, 0

	while len(geohash) < precision:
		if isEven:
			mid = sum(lngInterval[0:2]) / 2
			if longitude > mid:
				ch |= BITS[bit]
				lngInterval[0] = mid
			else:
				lngInterval[1] = mid
		else:
			mid = sum(latInterval[0:2]) / 2
			if latitude > mid:
				ch |= BITS[bit]
				latInterval[0] = mid
			else:
				latInterval[1] = mid

		isEven = not isEven

		if bit < 4:
			bit += 1
		else:
			geohash += BASE_32[ch]
			bit = 0
			ch = 0

	return geohash

def city2latlon(city, cursor = sqlite3.connect(db_path).cursor()):
	cities = cursor.execute("SELECT * FROM csv_table WHERE area LIKE '' and city LIKE '\"" + city + "%';").fetchall()
	return float(cities[0][4][1:-1]), float(cities[0][5][1:-1])

def latlon2city(latitude, longitude, cursor = sqlite3.connect(db_path).cursor()):
	cityLatlon = lambda city: (float(city[4][1:-1]), float(city[5][1:-1]))
	cityllSort = lambda cityll: cityll[1]
	cities = cursor.execute("SELECT * FROM csv_table WHERE geo_hash LIKE '\"" + latlon2geohash(latitude, longitude)[0:3] + "%';").fetchall()
	return sorted([(city, latlon2distance(*cityLatlon(city), latitude, longitude)) for city in cities], key = cityllSort)[0][0][2][1:-1]
