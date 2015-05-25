# -*- coding: utf8 -*-

from __future__ import unicode_literals

import json

from optimizer import Optimizer


class BruteForce(Optimizer):
    """
    Basic brute-force optimizer. Given that you have an infinite amount
    of time to wait, this optimizer will always find the best solution for your
    problem. Unfortunately, you don't have such time. Try something else.
    * `step`, float value, speed of search for the solution over the search
      space. Higher values will increase the speed, but lower the precision
      of solution found.
    """
    def __init__(self, name, problem, step=1.0):
        super(BruteForce, self).__init__(
            solverType='optimizer', name=name,
            problem=problem)
        self._step = float(step)
        self._scope = problem.getScope()

    def _genNext(self):
        """
        Generate the next solution to try out.
        * solution:list, last generated solution
        * i:int, the index of the variable to increment
        """
        def inc(solution, i=0):
            done = False
            if i >= len(solution):
                return True
            if solution[i] + self._step > self._scope[i][2]:
                done = inc(solution, i + 1)
                solution[i] = self._scope[i][1]
            else:
                solution[i] += self._step
            return done

        # solution = [min, min, min, ...]
        solution = [var[1] for var in self._scope]
        done = False
        while not done:
            done = inc(solution)
            yield solution

    def run(self):
        """
        Visualization data exchange protocol:
        Json encoded object having 3 fields: `current` `best` and `done`
        The two first holds an object with the fields `solution` (that contains
        the actual solution) and `evaluation` (that contains the evaluation for
        this solution).
        The latter is a boolean indicating if the process is terminated.
        """
        best = None
        best_sol = None
        for solution in self._genNext():
            evaluation = self._problem.evaluate(solution)
            self._log(
                'Evaluating: [%.3f] %s' % (evaluation, str(solution)))
            self._viz(json.dumps({
                'current': {'solution': solution, 'evaluation': evaluation},
                'best': {'solution': best_sol, 'evaluation': best}
            }))
            if best is None or self._problem.isBetter(evaluation, best):
                self._log(
                    '>>> [%.3f] %s is better!' % (evaluation, str(solution)),
                    timeout=0.1)
                best = evaluation
                best_sol = solution
        self._log(
            'Done. Best overall: [%.3f] %s' % (best, best_sol))
