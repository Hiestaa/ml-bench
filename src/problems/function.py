# -*- coding: utf8 -*-

from __future__ import unicode_literals

from optimization import Optimization


class Function(Optimization):
    """
    This optmimization problem is basically a function to be optmized (i.e.:
    the solver will try to find a global minimum). The parameters are:
    * `expression`, the function expression, that should be a python function
      of the variable `x`, a vector that has an entry for each dimension of the
      function
    * `dimension`, number of dimensions of the function
    * `rangeMin`, minimum value each dimension can have
    * `rangeMax`, maximum value each dimension can have
    """
    def __init__(self, name, expression, dimension, rangeMin, rangeMax):
        super(Optimization, self).__init__(
            problemTypes=['optimization'], name=name, dataset=None,
            dimension=dimension, rangeMin=rangeMin, rangeMax=rangeMax)
        self._dimension = dimension
        self._expression = expression
        self._range = (rangeMin, rangeMax)

    def evaluate(self, solution):
        """
        Evaluate a solution, returns a value that is higher if the solution
        is a better fit.
        * solution should be an array of float, of the same size than the array
          returned by the `getScope` function.
        """
        return eval(self._expression, {x: solution})

    def getScope(self):
        """
        Returns an array, where each variable of the optimization problem
        is associated with its range and type as a tuple (type, min, max).
        (variables have no name for the optimizer, only an index)
        """
        return [
            (float, self._range[0], self._range[1])
            for i in xrange(self._dimension)
        ]
