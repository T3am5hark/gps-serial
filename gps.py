from serial import Serial
from datetime import datetime, timedelta
import pytz
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
    def from_nmea(cls, latitude_str:str, ns_str:str,
                  longitude_str:str, ew_str: str):

        latitude = LatLong.parse_nmea_latitude(latitude_str)
        ns = cls.parse_nmea_ns(ns_str)
        longitude = LatLong.parse_nmea_longitude(longitude_str)
        ew = cls.parse_nmea_ew(ew_str)

        return cls(latitude, ns, longitude, ew)


def parse_msg(bytes):
    # Convert to string, strip carriage return chars
    msg = bytes.decode('utf-8').replace('\r\n', '')
    fields = msg.split(',', 1000)
    return msg, fields


def latlong_to_decimal_degrees(str):
    major = float(str[0:2])
    minutes = float(str[2:])

    decimal_degrees = major + minutes/60.0
    return decimal_degrees


def utc_to_datetime(utc_str: str):
    hh = int(utc_str[0:2])
    mm = int(utc_str[2:4])
    ss = int(utc_str[4:6])
    us = 10000*int(utc_str[7:8]) if len(utc_str) > 6 else 0

    dt_now = datetime.now().astimezone(pytz.utc)

    # Handle case where the passed-in timestamp is from yesterday
    # but the time lag causes datetime.now() to be a day later by
    # subtracting a day from now.
    if dt_now.hour < 2 and hh > 21:
        dt_now += timedelta(days=-1)

    dt = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day,
                  hour=hh, minute=mm, second=int(ss), microsecond=us)

    # Cast as UTC time
    dt = pytz.utc.localize(dt)

    return dt


class Message_GPGGA:

    def __init__(self, fields):
        if fields[0] != '$GPGGA':
            raise ValueError('Not a $GPGGA message')

    @classmethod
    def from_bytes(cls, bytes):
        msg, fields = parse_msg(bytes)
        return Message_GPGGA(fields)


class GpsReceiver:

    DEFAULT_BAUD = 2000000
    DEFAULT_DEVICE = '/dev/ttyACM0'
    DEFAULT_RECORDED_SENTENCES = ['$GPGGA',]

    def __init__(self, ser: Serial = None):
        if ser is None:
            ser = Serial(self.DEFAULT_DEVICE, self.DEFAULT_BAUD,
                         timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
        self.ser = ser

    def next_message(self):
        bytes = self.ser.readline()
        msg, fields = parse_msg(bytes)

        return msg, fields

