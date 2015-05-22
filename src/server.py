# -*- coding: utf8 -*-

from __future__ import unicode_literals
import time
import argparse
import logging

import tornado
from tornado.web import Application
from tornado.ioloop import IOLoop


from handlers.templatesHandler import TemplatesHandler
from handlers.problemsHandler import ProblemsHandler
from handlers.solversHandler import SolversHandler
from tools import log
from tools import model
from conf import Conf


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the server for the web-ui report",
        prog="server.py")
    parser.add_argument('--verbose', '-v', action="count",
                        help="Set console logging verbosity level. Default \
displays only ERROR messages, -v enable WARNING messages, -vv enable INFO \
messages and -vvv enable DEBUG messages. Ignored if started using daemon.",
                        default=0)
    parser.add_argument('-q', '--quiet', action="store_true",
                        help="Remove ALL logging messages from the console.")
    parser.add_argument('-l', '--log', action="store",
                        help="Change the path of the log file, default \
is log/server.log", default='../log/server.log')
    return parser.parse_args()


def run():
    ns = parse_args()

    log.init(ns.verbose, ns.quiet, logpath=ns.log)

    server_routes = [
        (r"/api/problems/([a-zA-Z_.-]+)/?", ProblemsHandler),
        (r"/api/solvers/([a-zA-Z_.-]+)/?", SolversHandler),
        (r"/([a-zA-Z_.-]+)?/?", TemplatesHandler)
    ]

    server_settings = {
        "cookie_secret": "101010",  # todo: generate a more secure token
        "template_path": "http/templates/",
        "static_path": "http/assets",
        "static_url_prefix": "/assets/",
        # allow to recompile templates on each request, enable autoreload
        # and some other useful features on debug. See:
        # http://www.tornadoweb.org/en/stable/guide/running.html#debug-mode
        "debug": Conf['state'] == 'DEBUG'
    }

    # start the server.
    logging.info("Server Starts - %s state - %s:%s"
                 % (Conf['state'], 'localhost', Conf['server']['port']))

    application = Application(server_routes, **server_settings)
    application.listen(Conf['server']['port'])

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt: exiting now.")

if __name__ == '__main__':
    run()
