# -*- coding: utf8 -*-

from __future__ import unicode_literals

### Initialize the logging system
import logging
import os

from logging.handlers import RotatingFileHandler
import logging

from conf import Conf
from config import termColors


class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)
        self.DEFAULT_COLOR = termColors.IWhite
        self.COLORS = {
            logging.DEBUG: termColors.White,
            logging.INFO: termColors.Green,
            logging.WARNING: termColors.BYellow,
            logging.ERROR: termColors.Red,
            logging.CRITICAL: termColors.BIRed
        }

    def format(self, record):
        color = self.COLORS[record.levelno] if record.levelno in self.COLORS \
            else self.DEFAULT_COLOR
        if not isinstance(record.msg, unicode):
            record.msg = repr(record.msg)
        record.msg = color + record.msg + termColors.Color_Off
        message = logging.Formatter.format(self, record)
        return message\
            .replace(
                record.levelname,
                '%s%s%s'
                % (termColors.Purple, record.levelname, termColors.Color_Off))\
            .replace(
                record.filename,
                '%s%s%s'
                % (termColors.Cyan, record.filename, termColors.Color_Off))


def init(verbose=0, quiet=False, logpath='log/server.log', colored=True):
    """
    Initialize the logger
    * verbose (int) specify the verbosity level of the standart output
      0 (default) ~ ERROR, 1 ~ WARN & WARNING, 2 ~ INFO, 3 ~ DEBUG
    * quiet (boolean) allow to remove all message written on the standart
                        output whatever is the verbosity lvl
    * logpath (string) the path to the file where logs will be written
    * colored (boolean) whether or not using colors to write on stdout
    """
    verbose_levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
        4: 1
    }

    tree = []
    for folder in os.path.split(logpath)[:-1]:
        tree.append(folder)
        if not os.path.exists(os.path.join(*tree)):
            os.mkdir(os.path.join(*tree))

    logger = logging.getLogger()
    logger.propagate = False
    logger.setLevel(min([Conf['log']['fileLevel'],
                         verbose_levels[verbose]]))

    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: ' +
        '%(filename)s:%(funcName)s[%(lineno)d] :: %(message)s')
    file_handler = RotatingFileHandler(logpath, 'w', 10000000, 10)
    file_handler.setLevel(Conf['log']['fileLevel'])
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if not quiet:
        Formatter = ColorFormatter if colored else logging.Formatter
        formatter = Formatter(
            '%(levelname)s :: %(filename)s :: %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(verbose_levels[verbose])
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logging.info("=" * 80)
    logging.info('Logging system started: verbose=%d, quiet=%s' %
                 (verbose, str(quiet)))
