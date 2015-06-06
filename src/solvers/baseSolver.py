# -*- coding: utf8 -*-

from __future__ import unicode_literals

from multiprocessing import Process, Pipe
import time
import random

from mlbExceptions import SolverException
from tools import utils


class Solution(Exception):
    """
    Base class for the solution of any problem, found by any type of solver.
    Raise an instance of this class (or any sub-class) at any time during
    the execution of the solving algorithm when the solution is found.
    This will terminate the solver process, save the solution and send it to
    the client-side code.
    """
    def __init__(self):
        super(Solution, self).__init__()

    def toJSON(self):
        """
        This function is supposed to return a JSON-compatible dict-like object.
        It will be saved into the `solutions` collection into db along with all
        the problem and solver related informations.
        """
        raise NotImplementedError()


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
        self._ignoredLogInfoSent = False
        self._vizReader, self._vizWriter = Pipe(False)
        self._lastVizWrite = time.time()
        self._msrReader, self._msrWriter = Pipe(False)
        self._lastMsrWrite = time.time()
        self._start_t = time.time()
        self._nbSteps = 0
        self._startTime = None

    def getLogOutput(self):
        return self._logReader

    def getVizOutput(self):
        return self._vizReader

    def getMeasureOutput(self):
        return self._msrReader

    def _log(self, message, timeout=0.1, force=False, level=0):
        """
        Log a message to the log writer. The message can be any json-dumpable
        object.
        If `force` is left to False, the function **will not** be reliable.
        If a message has been already sent in the last `timeout` second, the
        message will be discarded to limit the write rate over the socket.
        Set `force` to True to disable this behaviour (or `timeout` to 0)
        `level` is the level of the log message, where higher values mean more
        critical message. Values should range in [0, 10].
        """
        # print("[LOG][to=%.3fs][force=%s] %s"
        #       % (timeout, str(force), message))
        if force or time.time() - self._lastLogWrite > timeout:
            self._logWriter.send({'message': message, 'level': level})
            if not force:
                self._lastLogWrite = time.time()
            self._ignoredLogInfoSent = False
        elif not self._ignoredLogInfoSent:
            self._ignoredLogInfoSent = True
            self._logWriter.send({'message': '[...]', 'level': 0})

    def _viz(self, message, timeout=0.1, force=False):
        """
        Log a message to the viz writer.
        If `force` is left to False, the function **will not** be reliable.
        If a message has been already sent in the last `timeout` second, the
        message will be discarded to limit the write rate over the socket.
        Set `force` to True to disable this behaviour (or `timeout` to 0)
        Note: `message` is expected to be a dict.
        """
        print("[VIZ][to=%.3fs][force=%s] %s"
              % (timeout, str(force), message))
        if force or time.time() - self._lastVizWrite > timeout:
            message = utils.extends(message, **self._problem.viz(message))
            self._vizWriter.send(message)
            if not force:
                self._lastVizWrite = time.time()

    def _msr(self, message, timeout=1.0, force=False):
        """
        Log measured data to the measurement pip writer.
        If `force` is left to False, the function **will not** be reliable.
        If a message has been already sent in the last `timeout` second, the
        message will be discarded to limit the write rate over the socket.
        Set `force` to True to disable this behaviour (or `timeout` to 0)
        """
        if force or time.time() - self._lastMsrWrite > timeout:
            self._msrWriter.send(message)
            if not force:
                self._lastMsrWrite = time.time()

    def initialize(self):
        """
        Called once right before starting the solver.
        Warning: this will not be called by the object's constructor,
        creating new object properties won't work there.
        """
        self._startTime = time.time()

    def initView(self):
        """
        Any data that should be sent to initialize the solver view should be
        returned as a dict by this function.
        """
        return {}

    def measure(self, lastMeasure=None, m=None):
        """
        Save data related to the state of the algorithm at this exact moment.
        This function will be called automatically if the 'step-by-step'
        implementation of the solver is used. Otherwise, it's up to the
        programmer to call this function when relevant.
        When overriding this function, at the end of the measurement process,
        call:
        `return super(<ClassName>, self).measure(lastMeasure, currentMeasure)`
        to let the parent class add required field and send the data over the
        socket and save them for later use.
        Measurements names starting with `_` are reserved (may be overrided).
        Note: using the `step-by-step` method, the `measure` function will
        ALWAYS be called AFTER the first step.
        * lastMeasure:mixed, the previous measure performed. None if
          this function is called for the first time.
        * m:dict, any measurement data already performed
        Returns a dict where measurement keys are asociated with corresponding
        values.
        """
        if m is None:
            m = {}
        m['_time'] = time.time()
        if lastMeasure is not None:
            m['_stepDuration'] = time.time() - lastMeasure['_time']
        else:
            m['_stepDuration'] = time.time() - self._start_t
        self._msr(m)
        return m

    def step(self):
        """
        If the 'step-by-step' implementation of the solver is used, this
        function will be called automatically to perform one step of the
        solving process. `measure` will automatically be called between two
        steps.
        Return the boolean True to end the process (if no solution is found),
        or raise a `Solution` instance.
        """
        raise NotImplementedError()

    def solve(self):
        """
        There is two ways to implement a solver. The first is 'iterative',
        'step-by-step'. For this method, override the `step` function
        that will be called iteratively until the algorithm is
        done. This enable automatic performance and time measurements
        (via the `measure` function that requires to be implemented as well).

        The second method is to override this function (`solve`), in that case
        a single call should provide at the end the solution to the algorithm.
        This function will only be called once and no measurement will be
        performed automatically. You should call the function `measure` by
        yourself when relevant for your algorithm.

        In any case, to return the solution, raise the one of the subclass of
        the `Solution` class.

        To send data to the visualization code or the in-app log window, use
        respectively the `_log` and `_viz` functions, the messages sent here
        will be json-dumped and sent over the websocket to the client-side code
        """
        measure = None
        while not self.step():
            self._nbSteps += 1
            measure = self.measure(lastMeasure=measure)

    def run(self):
        self.initialize()
        self._viz({
            'initProblem': self._problem.initView(),
            'initSolver': self.initView()
        }, force=True)
        try:
            self.solve()
        except Solution as sol:
            print sol
