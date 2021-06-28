from event_recorder import SimpleEventRecorder
from gps import GpsReceiver
from time import sleep


def gps_main(sleep_time_s=0.2, print_all_to_screen=True):

    rec = SimpleEventRecorder()
    gps = GpsReceiver()

    logger = rec._logger

    logger.info(f'Starting loop with {sleep_time_s:.04}s wait')

    while True:

        msg, fields = gps.next_message()
        if print_all_to_screen:
            print(msg)

        rec.record_nmea_message(msg, fields)

        sleep(sleep_time_s)


if __name__ == '__main__':
    gps_main()
