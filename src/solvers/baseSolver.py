# -*- coding: utf8 -*-

from __future__ import unicode_literals

from multiprocessing import Process, Pipe

from exceptions import SolverException


class BaseSolver(Process):
    """
    Represents any solver class algorithm. This defines as well the interface
    of solver, common to all solver types.
    Any sub
    """
    def __init__(self, solverType, problem, fullName, parameters={}):
        """
        Initialize a new solver of the given type.
        * solverType:string, the type of this solver. Accepted values
          are: "optimizer", "clustering" or "classification".
        * problem:Problem subclass, that should implement the interface for
          this type of solver.
        * fullName:string, name of this solver, for identification purposes.
        * parameters:dict, the name of each parameter should be associated with
          its value.
        """
        super(BaseSolver, self).__init__(name='process-%s' % fullName)
        if not solverType in ['optimizer', 'clusterer', 'classifier']:
            raise SolverException(
                solverType, fullName, parameters,
                "Invalid solver type: %s" % solverType)
        self._solverType = solverType
        self._fullName = fullName
        self._problem = problem
        self._parameters = parameters
        self._pipeInput, self._pipeOutput = Pipe()

    def getPipeOutput(self):
        return self._pipeOutput

    def run(self):
        """
        Override this function in the subclasses, this will run the
        algorithm on a different system process.
        Data to be sent to the visualization code should be written at the
        input-side (parent-side) of the pipe and will be forwarded to the
        websocket connection by the websocket handler.
        """
        raise NotImplementedError()
