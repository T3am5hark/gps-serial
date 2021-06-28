from abc import abstractmethod
from datetime import datetime, timedelta
from gps import parse_msg, LatLong, utc_to_datetime
from log_utils import *


class NmeaRecorderAbstract:

    DEFAULT_CONFIG = {'$GPGGA': {'frequency': timedelta(seconds=10),
                                 'log_level': logging.DEBUG,
                                 'log_original': True},
                      }

    DUMMY_CONFIG = {'frequency': timedelta(seconds=600),
                    'log_level': logging.DEBUG,
                    'log_original': True}

    def __init__(self, config=DEFAULT_CONFIG):
        self._config = config

    @abstractmethod
    def record_nmea_message(self, msg, fields=None):
        pass


class SimpleEventRecorder(NmeaRecorderAbstract):

    def __init__(self, config=NmeaRecorderAbstract.DEFAULT_CONFIG,
                 logger=None, log_to_file=True):
        super(SimpleEventRecorder, self).__init__(config)

        if logger is None:
            logger = init_logging_screen()
            if log_to_file:
                logger = init_logging_file()

        self._logger = logger

        self._msg_timestamps = dict()

    def _should_update(self, nmea_sentence_label:str):

        # Not configured to record this sentence type
        if nmea_sentence_label not in self._config.keys():
            return False

        # No messages of this type yet recorded, grab this one
        if nmea_sentence_label not in self._msg_timestamps.keys():
            return True

        # Enough time has lapsed since last recording, grab this one
        last_timestamp = self._msg_timestamps.get(nmea_sentence_label, datetime.now)
        freq = self._config.get(nmea_sentence_label, self.DUMMY_CONFIG)['frequency']
        if datetime.now() - last_timestamp > freq:
            return True

        return False

    def record_nmea_message(self, msg, fields=None):

        if fields is None:
            _, fields = parse_msg(msg)

        if self._should_update(fields[0]):

            # Track most recent update
            self._msg_timestamps[fields[0]] = datetime.now()

            if fields[0] == '$GPGGA':
                try:
                    self._log_gpgga(msg, fields)
                except Exception as ex:
                    self._logger.exception(str(ex))

            else:
                pass

    def _log_gpgga(self, msg, fields):

        # Position Fix Indicator - check for valid GPS fix types
        if int(fields[6]) not in [1, 2, 6]:
            return

        # UTC from gps sentence
        gps_utc = str(utc_to_datetime(fields[1]))

        lat_long = LatLong.from_nmea(fields[2], fields[3],
                                     fields[4], fields[5])

        latitude = lat_long.latitude
        longitude = lat_long.longitude

        sats_used = int(fields[7])

        altitude = float(fields[8])

        log_str = f'{gps_utc}, {latitude[0]} {latitude[1].name[0]}, {longitude[0]} {longitude[1].name[0]}, ' \
            f'{altitude:.04f}, {sats_used}'

        config = self._config.get('$GPGGA', self.DUMMY_CONFIG)

        self._logger.log(config['log_level'], log_str)

        if config['log_original']:
            self._logger.log(config['log_level'], msg)
