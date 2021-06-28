from enum import Enum


class NorthSouth(Enum):
    NORTH = 0
    SOUTH = 1


class EastWest(Enum):
    EAST = 0
    WEST = 1


class LatLong:

    def __init__(self,
                 latitude: float, ns: NorthSouth,
                 longitude: float, ew: EastWest):
        self._lat = latitude
        self._ns = ns
        self._lng = longitude
        self._ew = ew

    @property
    def latitude(self):
        return self._lat, self._ns

    @property
    def longitude(self):
        return self._lng, self._ew

    @property
    def latlong(self):
        return self._lat, self._ns, self._lng, self._ew

    @property
    def map_friendly_latlong(self):
        ns_char = self._ns.name[0]
        ew_char = self._ew.name[0]
        latlong_str = '({}{}, {}{})'.format(self._lat, ns_char, self._lng, ew_char)
        return latlong_str

    @staticmethod
    def parse_nmea_latitude(latitude_str: str):
        degrees = float(latitude_str[0:2])
        minutes_of_arc = float(latitude_str[2:])

        return degrees + minutes_of_arc / 60.0

    @staticmethod
    def parse_nmea_longitude(longitude_str: str):
        degrees = float(longitude_str[0:3])
        minutes_of_arc = float(longitude_str[3:])

        return degrees + minutes_of_arc / 60.0

    @staticmethod
    def parse_nmea_ns(ns_str: str):
        if ns_str.lower()[0] == 'n':
            ns = NorthSouth.NORTH
        elif ns_str.lower()[0] == 's':
            ns = NorthSouth.SOUTH
        else:
            raise ValueError('Input string does not match expected format (N,S)')

        return ns

    @staticmethod
    def parse_nmea_ew(ew_str: str):
        if ew_str.lower()[0] == 'e':
            ew = EastWest.EAST
        elif ew_str.lower()[0] == 'w':
            ew = EastWest.WEST
        else:
            raise ValueError('Input string does not match expected format (E,W)')

        return ew

    @classmethod
    def from_nmea(cls, latitude_str: str, ns_str: str,
                  longitude_str: str, ew_str: str):

        latitude = LatLong.parse_nmea_latitude(latitude_str)
        ns = cls.parse_nmea_ns(ns_str)
        longitude = LatLong.parse_nmea_longitude(longitude_str)
        ew = cls.parse_nmea_ew(ew_str)

        return cls(latitude, ns, longitude, ew)
