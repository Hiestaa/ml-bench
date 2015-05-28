# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
import time
import json

from tornado.web import HTTPError, asynchronous
from tornado.websocket import WebSocketHandler
from tornado import gen
import gevent
from gevent.socket import wait_read, timeout

from tools import model
from mlbExceptions import SolverException
from tools.utils import lcFirst


class RunSolverHandler(WebSocketHandler):
    """Handle requests related to the running of the solvers."""
    def initialize(self):
        logging.info("Initializing")
        self._runningSolver = None

    def open(self):
        logging.info("Websocket created.")

    @gen.coroutine
    def onRunSolver(self, solverId):
        solver = yield model.getService('solvers').getById(solverId)
        logging.info("Runnning %s: %s" % (solver['type'], solver['name']))

        # dynamic solver/problem module import
        solverImplemModule = __import__(
            'solvers.%s' % lcFirst(solver['implementation']),
            fromlist=[solver['implementation']])
        problemImplemModule = __import__(
            'problems.%s' % lcFirst(solver['problem']['implementation']),
            fromlist=[solver['problem']['implementation']])
        # instanciate problem with the right parameters
        problemInstance = getattr(
            problemImplemModule, solver['problem']['implementation'])(
                solver['problem']['name'], solver['problem']['dataset'],
                **solver['problem']['parameters'])
        # instanciate solver with the right parameters
        solverInstance = getattr(solverImplemModule, solver['implementation'])(
            solver['name'], problemInstance, **solver['parameters'])
        self._runningSolver = solverInstance

        # run the solver algorithm on a different process
        logging.info("Starting process")
        solverInstance.start()

        # spawn the greenlets that will forward data read on the pipes to
        # the websocket
        logging.info("Spawning forwarders")
        logThread = gevent.spawn(
            self.pipe2SocketForwarder, 'log', solverInstance.getLogOutput())
        vizThread = gevent.spawn(
            self.pipe2SocketForwarder, 'viz', solverInstance.getVizOutput())
        gevent.joinall([logThread, vizThread])

    def onKillRunningSolver(self):
        if self._runningSolver:
            self._runningSolver.terminate()
        else:
            logging.warning("No running solver!")

    def on_message(self, message):
        """
        Message sent to this handler via the websocket connection should be
        json-encoded objects with the following structure:
        {
            "action": "<action>", # where <action> can be either run or kill
            "solver": "<solverId>", # the id of the solver to run
        }
        If <action> is "run", this will initiate a new run for the specified
        solver. As the solver is running, messages will be sent to the client
        through the websocket to send log and visualization information. See
        `pipe2SocketForwarder` function for more details about the format of
        these messages.
        Note: an exception will be thrown and the message '{error: "[...]"}'
        will be sent if a solver is already running.
        If <action> is "kill", this will kill any running solver (whatever is
        specified in the "solver" field). You should use this action before
        starting another one to avoid any error.
        """
        logging.info("Received message: %s" % message)
        message = json.loads(message)
        if message['action'] == 'run' and self._runningSolver is not None:
            raise MLBenchException("Mis-formatted message: %s" % str(message))
        if message['action'] == 'run':
            if not 'solver' in message:
                raise MLBenchException(
                    "Mis-formatted message: %s" % str(message))
            self.onRunSolver(message['solver'])
        if message['action'] == 'kill':
            self.onKillRunningSolver()

    def on_close(self):
        logging.info("Websocket closed.")

    @gen.coroutine
    def pipe2SocketForwarder(self, name, pipe):
        """
        Forward data read from the log and visualization pipes to the
        websocket.
        The format of the messages sent is a json-encoded object with the
        following structure:
        {
            <name>: <object sent over the pipe>
        }
        Where `<name>` can be either "log" or "viz".
        The format of the objects are defined in each solver.
        """
        logging.info("Starting pipe to socket forwarder...")
        loops = 0
        start_t = time.time()
        # the loop will stop once the solver is killed or the task is finished
        while self._runningSolver.is_alive() or pipe.poll():
            loops += 1
            # wait 'till something is available to read
            logging.debug("Waiting for something to read on the pipe...")
            try:
                wait_read(pipe.fileno(), timeout=0)
            except timeout:
                # no data to read, no data to send, just wait and try again
                yield gen.sleep(0.1)
                continue
            # read the data (shouldn't block as called wait_read)
            msg = pipe.recv()
            # send the json-encoded data
            data = json.dumps({name: msg})
            logging.debug("Sending data: %s" % (data))
            self.write_message(data)
            # return control to tornado's ioloop
            yield gen.sleep(0)

        # once the loop is stopped, log some messages
        logging.info("Stopping forwarder -- running solver is not alive \
anymore. ")
        logging.info("Stats: %d loops done in %.3fs"
                     % (loops, time.time() - start_t))
