# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
import sys
import os
import json
import time
from datetime import datetime
from threading import Lock
from motor import MotorClient
from pymongo.errors import ConnectionFailure
from pymongo.son_manipulator import SONManipulator

from conf import Conf
from services.baseService import Service
from tools.utils import dateFormat, sizeFormat, getFolderSize


class ObjectIdManipulator(SONManipulator):
    def transform_outgoing(self, son, collection):
        if '_id' in son:
            son[u'_id'] = str(son[u'_id'])
        return son


class ModelException(Exception):
    pass


### This class is the interface with the mongodb api.
class Model(object):
    """
    This class is the interface with the mongodb api.
    It is used to retrieve text to be used by the nlp algorithm from the loops
    collection and to cache items like account list, locations or
    generated reports
    It manages its own back-up system by creating DB dumps every week
    (or any configured delay)
    """
    def __init__(self):
        super(Model, self).__init__()
        logging.info("Starting mongo client...")
        # create connection

        success = False
        retry = 0
        while not success:
            try:
                self._connection = MotorClient(
                    host=Conf['database']['host'],
                    port=Conf['database']['port'])
                logging.info("Connection succeeded!")
                success = True
            except ConnectionFailure as e:
                logging.warning("MongoDB Server connection failed on %s:%s"
                                % (Conf['database']['host'],
                                   Conf['database']['port']))
                logging.warning(repr(e))
                retry += 1
                if retry > 10:
                    raise ModelException("Max connection retries to MongoDB \
server (%d) exceeded." % (10))

        self._db = self._connection[Conf['database']['dbName']]
        self._db.add_son_manipulator(ObjectIdManipulator())

        self._services = {
            # 'video':  VideoService(self._db),
            # 'tag': TagService(self._db),
            # 'album': AlbumService(self._db)
        }

    def getService(self, serviceName):
        """
        Return a service that matches the given service name.
        The convention is that each service's name is the same than
        the name of the module (file) into which it is defined, "Service"
        removed. The name of the class that implements it should be the same
        but starting with a capital letter.
        For instance: the service "hello" should be a class named
        "HelloService" found in the module "helloService"
        """
        def ucFirst(s):
            return s[0].upper() + s[1:]
        # if the service is already instanciated, return it
        if serviceName in self._services:
            return self._services[serviceName]
        # dynamically import the service
        serviceModule = __import__(
            'services.%sService' % serviceName,
            fromlist=[ucFirst(serviceName + "Service")])
        # instanciate it, save the instance for a later use
        self._services[serviceName] = getattr(
            serviceModule, ucFirst(serviceName + "Service"))(self._db)
        # return the instance
        return self._services[serviceName]


# this module is a singleton
# This object should not be accessed directly, use getInstance instead.
_instance = None
# will be used to lock the instance while initializing it.
_lock = Lock()


def getInstance():
    global _instance
    global _lock
    if _instance is None:
        with _lock:
            # re-test the _instance value, avoiding the case where another
            # thread did the initialization between the previous test and the
            # lock
            if _instance is None:
                _instance = Model()
    return _instance


def getService(service):
    return getInstance().getService(service)
