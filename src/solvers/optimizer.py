# -*- coding: utf8 -*-

from __future__ import unicode_literals

import time

from baseSolver import BaseSolver, Solution


class OptimizationSolution(Solution):
    """
    Represents a solution found by an optimizer.
    """
    def __init__(self, solution, evaluation):
        super(OptimizationSolution, self).__init__()
        self._solution = solution
        self._evaluation = evaluation


class Optimizer(BaseSolver):
    """Any optimizer should inherit from this base class"""
    def __init__(self, name, problem):
        super(Optimizer, self).__init__(
            solverType='optimizer', name=name,
            problem=problem)
        self._start_t = time.time()
        self._scope = problem.getScope()

    def specMeasure(self, lastMeasure):
        """
        Override this function to keep generic optimizer measures.
        Returns a dict where the entry 'time' should NOT exist (will
        be overrided)
        * lastMeasure:mixed, the previous measure performed. None if
          this function is called for the first time.
        """
        return {}

    def measure(self, lastMeasure=None):
        """
        Default mesurement performed automatically during the
        process of solving an optimization problem.
        * lastMeasure:mixed, the previous measure performed. None if
          this function is called for the first time.
        """
        m = self.specMeasure(lastMeasure)
        m['time'] = time.time()
        if lastMeasure is not None:
            m['stepDuration'] = time.time() - lastMeasure['time']
        else:
            m['stepDuration'] = time.time() - self._start_t
        return m
