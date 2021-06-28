import logging
from sys import stderr
from datetime import datetime

DEFAULT_LOGGER_NAME = 'gps_logger'


def timestamp(fmt='%Y-%m-%d %H:%M:%S', dtime=None):
    if dtime is None:
        dtime = datetime.now()

    return dtime.strftime(fmt)


def filename_timestamp(dtime=None):
    return timestamp(fmt='%Y-%m-%d', dtime=dtime)


def init_logging_screen(logger=None, log_level=logging.DEBUG,
                        formatter=None, stream=stderr):
    if logger is None:
        logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    # logging
    logger.setLevel(log_level)
    # create formatter
    if formatter is None:
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler(stream=stream)
    ch.setLevel(log_level)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    return logger


def init_logging_file(logger=None,
                      log_level=logging.DEBUG,
                      formatter=None,
                      filename: str = None,
                      **kwargs):

    if logger is None:
        logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    if filename is None:
        filename = DEFAULT_LOGGER_NAME + '.{}.log'.format(filename_timestamp())

    # create formatter
    if formatter is None:
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')

    fh = logging.FileHandler(filename, **kwargs)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
