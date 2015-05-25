# -*- coding: utf8 -*-

from __future__ import unicode_literals

from optimization import Optimization

DEFAULT_EXP = 'sum(x[i] ** i for x in xrange(len(x)))'


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
    * `goal`, whether the function should be maximized or minimized. Accepted
      value are 'max', 'maxi', 'maxim', ... and '1'. All other value will
      result in the function being miminized.
    """
    def __init__(self, name, dataset, expression=DEFAULT_EXP,
                 dimension=10, rangeMin=0, rangeMax=100, goal='minimize'):
        super(Optimization, self).__init__(
            name=name, dataset=None,
            dimension=dimension, rangeMin=rangeMin, rangeMax=rangeMax,
            goal=goal)
        self._dimension = dimension
        self._expression = expression
        self._range = (rangeMin, rangeMax)
        self._goal = 1 if str(goal)[:3] == 'max' or str(goal) == '1' else -1

    def evaluate(self, solution):
        """
        Evaluate a solution, returns a value that is higher if the solution
        is a better fit.
        * solution should be an array of float, of the same size than the array
          returned by the `getScope` function.
        """
        return eval(self._expression, {x: solution})

    def isBetter(self, evaluation1, evaluation2):
        return evaluation1 * self._goal > evaluation2 * self._goal

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
