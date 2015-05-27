# -*- coding: utf8 -*-

from __future__ import unicode_literals

from multiprocessing import Process, Pipe
import time

from mlbExceptions import SolverException


class BaseSolver(Process):
    """
    Represents any solver class algorithm. This defines as well the interface
    of solver, common to all solver types.
    Any sub
    """
    def __init__(self, solverType, problem, name):
        """
        Initialize a new solver of the given type.
        * solverType:string, the type of this solver. Accepted values
          are: "optimizer", "clustering" or "classification".
        * problem:Problem subclass, that should implement the interface for
          this type of solver.
        * name:string, name of this solver, for identification purposes.
        """
        super(BaseSolver, self).__init__(name='process-%s' % name)
        if not solverType in ['optimizer', 'clusterer', 'classifier']:
            raise SolverException(
                solverType, name, parameters,
                "Invalid solver type: %s" % solverType)
        self._solverType = solverType
        self._name = name
        self._problem = problem
        self._logReader, self._logWriter = Pipe(False)
        self._lastLogWrite = time.time()
        self._vizReader, self._vizWriter = Pipe(False)
        self._lastVizWrite = time.time()

    def getLogOutput(self):
        return self._logReader

    def getVizOutput(self):
        return self._vizReader

    def _log(self, message, timeout=0.1, force=False):
        """
        Log a message to the log writer.
        If `force` is left to False, the function **will not** be reliable.
        If a message has been already sent in the last `timeout` second, the
        message will be discarded to limit the write rate over the socket.
        Set `force` to True to disable this behaviour (or `timeout` to 0)
        """
        # print("[LOG][to=%.3fs][force=%s] %s"
        #       % (timeout, str(force), message))
        if force or time.time() - self._lastLogWrite > timeout:
            self._logWriter.send(message)
            self._lastLogWrite = time.time()
#         else:
#             print "Discarded message, time since last message is: \
# %.3fs < %.3fs" % (time.time() - self._lastLogWrite, timeout)

    def _viz(self, message, timeout=0.1, force=False):
        """
        Log a message to the viz writer.
        If `force` is left to False, the function **will not** be reliable.
        If a message has been already sent in the last `timeout` second, the
        message will be discarded to limit the write rate over the socket.
        Set `force` to True to disable this behaviour (or `timeout` to 0)
        """
        # print("[VIZ][to=%.3fs][force=%s] %s"
        #               % (timeout, str(force), message))
        if force or time.time() - self._lastVizWrite > timeout:
            self._vizWriter.send(message)
            self._lastVizWrite = time.time()

    def run(self):
        """
        Override this function in the subclasses, this will run the
        algorithm on a different system process.
        Data to be sent to the visualization code should be written at the
        input-side (parent-side) of the pipe and will be forwarded to the
        websocket connection by the websocket handler.
        """
        raise NotImplementedError()
