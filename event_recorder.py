from abc import abstractmethod
from datetime import datetime, timedelta
from nmea_messages import NmeaMessage, NmeaGpgga

from log_utils import *

DEFAULT_CONFIG = {'$GPGGA': {'frequency': timedelta(seconds=30),
                             'log_level': logging.DEBUG,
                             'log_original': True},
                  }

DUMMY_CONFIG = {'frequency': timedelta(seconds=600),
                'log_level': logging.DEBUG,
                'log_original': True}


class EventTimer:

    def __init__(self, config=DEFAULT_CONFIG):
        self._config = config
        self._msg_timestamps = dict()

    def should_update(self, nmea_sentence_label: str):

        # Not configured to record this sentence type
        if nmea_sentence_label not in self._config.keys():
            return False

        # No messages of this type yet recorded, grab this one
        if nmea_sentence_label not in self._msg_timestamps.keys():
            return True

        # Enough time has lapsed since last recording, grab this one
        last_timestamp = self._msg_timestamps.get(nmea_sentence_label, datetime.now)
        freq = self._config.get(nmea_sentence_label, DUMMY_CONFIG)['frequency']
        if datetime.now() - last_timestamp > freq:
            return True

        return False

    def update(self, nmea_sentence_label: str):
        # Track most recent update
        self._msg_timestamps[nmea_sentence_label] = datetime.now()


class NmeaRecorderAbstract:

    def __init__(self, config=DEFAULT_CONFIG,
                 timer: EventTimer = None):
        self._config = config
        if timer is None:
            timer = EventTimer(config)

        self._timer = timer

    @abstractmethod
    def record_nmea_message(self, msg, fields=None):
        pass


class LoggingEventRecorder(NmeaRecorderAbstract):

    def __init__(self, config=DEFAULT_CONFIG,
                 timer: EventTimer = None,
                 logger=None, log_to_file=True,
                 log_location:str = '.'):
        super().__init__(config, timer)

        if logger is None:
            logger = init_logging_screen()
            if log_to_file:
                logger = init_logging_file(location=log_location)

        self._logger = logger

    def record_nmea_message(self, nmea_msg: NmeaMessage):

        message_type = nmea_msg.message_type
        if self._timer.should_update(message_type):

            self._timer.update(message_type)

            if message_type == '$GPGGA':
                try:
                    self._log_gpgga(nmea_msg)
                except Exception as ex:
                    self._logger.exception(str(ex))

            else:
                pass

    def _log_gpgga(self, msg: NmeaGpgga):

        if not msg.valid_position_fix:
            return

        lat_long = msg.lat_long

        latitude = lat_long.latitude
        longitude = lat_long.longitude

        log_str = f'{msg.gps_utc}, {latitude[0]} {latitude[1].name[0]}, {longitude[0]} {longitude[1].name[0]}, ' \
            f'{msg.altitude:.04f}, {msg.sats_used}'

        config = self._config.get('$GPGGA', None)

        if config is not None:

            self._logger.log(config['log_level'], log_str)

            if config['log_original']:
                self._logger.log(config['log_level'], msg.msg)


class CsvPositionRecorder(NmeaRecorderAbstract):
    FIELD_NAMES = ['timestamp', 'UTC_TimeStamp',
                   'latitude', 'northsouth',
                   'longitude', 'eastwest',
                   'altitude', 'satellites_used',
                   ]

    def __init__(self, config=DEFAULT_CONFIG,
                 timer: EventTimer = None,
                 fname: str = None,
                 location: str = '.'):
        super().__init__(config, timer)

        if fname is None:
            fname = 'gps_events.{}.csv'.format(timestamp())

        fname = location + '/' + fname

        self._fp = open(fname, 'w')

        self._write_column_headers()

    def _write_column_headers(self):

        header_line = ''
        for i, field in enumerate(self.FIELD_NAMES):
            header_line += field
            if i < len(self.FIELD_NAMES)-1:
                header_line += ','

        self._fp.write(header_line+'\n')
        self._fp.flush()

    def record_nmea_message(self, nmea_msg: NmeaMessage):

        message_type = nmea_msg.message_type
        if self._timer.should_update(message_type):

            self._timer.update(message_type)

            if message_type == '$GPGGA':
                self._write_gpgga(nmea_msg)
            else:
                pass

    def _write_gpgga(self, msg: NmeaGpgga):

        if not msg.valid_position_fix:
            return

        now = datetime.now()

        lat_long = msg.lat_long

        latitude = lat_long.latitude
        longitude = lat_long.longitude

        csv_str = f'{now}, {msg.gps_utc}, ' \
            f'{latitude[0]}, {latitude[1].name[0]}, ' \
            f'{longitude[0]}, {longitude[1].name[0]}, ' \
            f'{msg.altitude:.04f}, {msg.sats_used}\n'

        self._fp.write(csv_str)
        self._fp.flush()
