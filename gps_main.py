from event_recorder import LoggingEventRecorder, CsvPositionRecorder
from gps import GpsReceiver
from nmea_messages import NmeaMessage
from time import sleep
from datetime import timedelta
import logging

CONFIG = {'$GPGGA': {'frequency': timedelta(seconds=10),
                     'log_level': logging.DEBUG,
                     'log_original': False},
          }

LOG_LOCATION = '/home/pi/jdm/gps-serial/logs'


def gps_main(sleep_time_s=0.1, print_all_to_screen=True):

    log = LoggingEventRecorder(config=CONFIG, log_location=LOG_LOCATION)
    csv = CsvPositionRecorder(config=CONFIG, location=LOG_LOCATION)

    # recorders = [log, csv]
    recorders = [csv, ]

    gps = GpsReceiver()

    logger = log._logger

    logger.info(f'Starting loop with {sleep_time_s:.04}s wait')

    while True:

        bytes = gps.next_message()

        if print_all_to_screen:
            print(str(bytes))

        nmea = NmeaMessage.bytes_to_nmea_message(bytes)

        for rec in recorders:
            rec.record_nmea_message(nmea)

        sleep(sleep_time_s)


if __name__ == '__main__':
    gps_main()
