from abc import abstractmethod
from lat_long import LatLong
from datetime import datetime, timedelta
import pytz


class NmeaMessage:

    def __init__(self, msg, fields):

        if fields is None:
            msg, fields = self.parse_msg(msg)

        self.msg = msg
        self.fields = fields

    @property
    def message_type(self):
        # The first entry in the Nmea message declares its type
        return self.fields[0]

    @classmethod
    def parse_msg(cls, byte_seq):
        # Convert to string, strip carriage return chars
        msg = byte_seq.decode('utf-8').replace('\r\n', '')
        fields = msg.split(',', 1000)
        return msg, fields

    @classmethod
    def utc_to_datetime(cls, utc_str: str):
        hh = int(utc_str[0:2])
        mm = int(utc_str[2:4])
        ss = int(utc_str[4:6])
        us = 10000 * int(utc_str[7:8]) if len(utc_str) > 6 else 0

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

    @classmethod
    def bytes_to_nmea_message(cls, byte_seq):

        msg, fields = NmeaMessage.parse_msg(byte_seq)

        if fields[0] == '$GPGGA':
            return NmeaGpgga(msg, fields)
        else:
            return NmeaMessage(msg, fields)


class NmeaGpgga(NmeaMessage):

    def __init__(self, msg, fields):

        super().__init__(msg, fields)

        fields = self.fields

        try:
            self._gps_utc = NmeaMessage.utc_to_datetime(fields[1])
            self._sats_used = int(fields[7])
        except Exception as ex:
            # If the gps receiver isn't seeing any satellites, it may return blank
            # timestamps.
            self._gps_utc = datetime.now().astimezone(pytz.utc)
            self._sats_used = 0

        if self.valid_position_fix:


            self._lat_long = LatLong.from_nmea(fields[2], fields[3],
                                               fields[4], fields[5])

            self._altitude = float(fields[9])

        else:
            self._lat_long = None
            self._altitude = None

    @property
    def gps_utc(self):
        return self._gps_utc

    @property
    def lat_long(self):
        return self._lat_long

    @property
    def sats_used(self):
        return self._sats_used

    @property
    def altitude(self):
        return self._altitude

    @property
    def position_fix_code(self):
        return int(self.fields[6])

    @property
    def valid_position_fix(self):
        # These are consisered valid position fixes
        return True if self.position_fix_code in [1, 2, 6] else False

