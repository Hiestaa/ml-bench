# -*- coding: utf8 -*-

from __future__ import unicode_literals

import json
import math
import time
import logging
import pkgutil
from datetime import datetime
import os

"""
This module contains miscelaneous functions that can be useful anywhere in
the project.
"""


def genModules(pkgs):
    """
    Recursively yield all the modules in the given package.
    """
    logging.info("Listing modules in package: %s" % str(pkgs))
    next_level = []
    for (module_loader, name, is_pkg) in pkgutil.iter_modules(
            path=pkgs):
        if is_pkg:
            next_level.append(name)
        else:
            logging.info(">> Found submodule: %s" % name)
            yield name
    if len(next_level) > 0:
        for name in genModules(next_level):
            yield name


def sizeFormat(sizeInBytes):
    """
    Format a number of bytes (int) into the right unit for human readable
    display.
    """
    size = float(sizeInBytes)
    if sizeInBytes < 1024:
        return "%.0fB" % (size)
    if sizeInBytes < 1024 ** 2:
        return "%.3fKb" % (size / 1024)
    if sizeInBytes < 1024 ** 3:
        return "%.3fMb" % (size / (1024 ** 2))
    else:
        return "%.3fGb" % (size / (1024 ** 3))


def getFolderSize(path, formatted=False):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    if formatted:
        return sizeFormat(total_size)
    return total_size


def timeFormat(timestamp):
    """
    Format timestamp (nb of sec, float) into the right unit for human readable
    display.
    """
    if timestamp < 1:
        return "%.0fms" % (timestamp * 1000)
    if timestamp < 60:
        return "%.0fs" % (timestamp)
    if timestamp < 60 * 60:
        return "%.0fmin, %.0fs" % (math.floor(timestamp / 60), timestamp % 60)
    if timestamp < 60 * 60 * 24:
        return "%.0fh, %.0fmin, %.0fs" \
            % (math.floor(timestamp / (60 * 60)),
               math.floor((timestamp / 60) % 60),
               timestamp % 60)
    else:
        return "%.0fd, %.0fh, %.0fmin, %.0fs" \
            % (math.floor(timestamp / (60 * 60 * 24)),
               math.floor((timestamp / (60 * 60)) % 24),
               math.floor((timestamp / 60) % 60),
               timestamp % 60)


def dateFormat(timestamp):
    """
    Format timestamp (nb of sec, float) into a human-readable date string
    """
    return datetime.fromtimestamp(
        int(timestamp)).strftime('%a %b %d, %Y - %H:%M')


def statusFormat(status):
    """
    Given the content of the status file, returns a human readable string
    that displays the status of the server.
    """
    if status is None:
        return "Status file does not exist. Daemon never started?"
    if not type(status) is dict:
        status = json.loads(status)
    if status['status'] == 'running':
        return "Status = running for %s. Started on: %s, PID=%s" \
            % (timeFormat(time.time() - status['start_ts']),
               status['start_date'], status['pid'])
    if status['status'] == 'stopped':
        return "Status = stopped since %s." % status['stop_date']


def parseISODate(date):
    """
    Parse the given date in string ISO format and returns a timestamp (float)
    in seconds.
    * date:string should have the format: '%Y-%m-%dT%H:%M:%S.***Z'
    """
    return time.mktime(datetime.strptime(
        date.split('.')[0],  # remove milliseconds
        "%Y-%m-%dT%H:%M:%S").timetuple())


def extends(dictionnary, **kwargs):
    """
    For each kwarg, will check if the key already exist in var,
    create it and set the given value if not.
    dictionnary is expected to be a dict
    Returns the extended dictionnary.
    """
    for k, v in kwargs.iteritems():
        if not k in dictionnary:
            dictionnary[k] = v
    return dictionnary


def clamp(val, mini, maxi):
    """
    Returns val, unless val > maxi in which case mini is returned
    or val < mini in which case maxi is returned
    """
    return max(mini, min(maxi, val))


def lcFirst(s):
    """
    Returns a copy of the string with the first letter lowercased
    """
    return s[0].lower() + s[1:]


def ucFirst(s):
    """
    Returns a copy of the string with the first letter uppercased
    """
    return s[0].upper() + s[1:]
