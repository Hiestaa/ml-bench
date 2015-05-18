# -*- coding: utf8 -*-

from __future__ import unicode_literals

from baseProblem import BaseProblem


class Optimization(BaseProblem):
    """
    Base class for any optimization problem. An optimizer solver can only
    work on problem classes that inherit from this one.
    All the methods of this class should be overrided.
    """
    def __init__(self, name, dataset=None, **kwargs):
        super(Optimization, self).__init__(
            problemTypes=['optimization'], name=name, dataset=dataset,
            **kwargs)

    def evaluate(self, solution):
        """
        Evaluate a solution, returns a value that is higher if the solution
        is a better fit.
        * solution should be an array of float, of the same size than the array
          returned by the `getScope` function.
        """
        raise NotImplementedError()

    def getScope(self):
        """
        Returns an array, where each variable of the optimization problem
        is associated with its range and type as a tuple (type, min, max).
        (variables have no name for the optimizer, only an index)
        """
        raise NotImplementedError()
