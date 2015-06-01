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
        self._scope = problem.getScope()
