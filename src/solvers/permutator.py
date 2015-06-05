# -*- coding: utf8 -*-

from __future__ import unicode_literals

import time
import itertools

from optimizer import OptimizationSolution
from bruteForce import BruteForce


class Permutator(BruteForce):
    """
    Basic optimizer by permutatons. Given that you have an infinite amount
    of time to wait, this optimizer will always find the best solution for your
    problem. Unfortunately, you don't have such time. Try something else.
    It is slightly more efficient than a basic brute-force optimizer since
    it does not try all the solutions that have duplicated values in it. To be
    used for problems where duplicated values doesn't make any sence.
    Note that the problem's scope may be extended. The maximum range among all
    values in the scope is used for each variable (the minimum range width
    still being the number of variable)
    * `step`, int value, speed of search for the solution over the search
      space. Higher values will increase the speed, but lower the precision
      of solution found.
    """
    def __init__(self, name, problem, step=1):
        super(Permutator, self).__init__(
            name=name, problem=problem, step=step)
        print " > Testing permutations only."

    def _genNext(self):
        """
        Generates the next solution to try out.
        """
        rng = [None, None, int(self._step)]
        for var in self._scope:
            if rng[0] is None or rng[0] > var[1]:
                rng[0] = var[1]
            if rng[1] is None or rng[1] < var[2]:
                rng[1] = var[2]
        if (rng[1] - rng[0]) / self._step < len(self._scope):
            rng[1] = rng[0] + len(self._scope) * self._step
        for solution in itertools.permutations(
                range(*[int(x) for x in rng]), r=len(self._scope)):
            yield solution
