# -*- coding: utf8 -*-

from __future__ import unicode_literals

import time

from optimizer import Optimizer, OptimizationSolution


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
        super(BruteForce, self).__init__(name=name, problem=problem)
        self._step = float(step)
        self._bestSol = None
        self._solGenerator = self._genNext()
        print "Starting Bruteforce optimizer."

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
            yield solution
            done = inc(solution)

    def measure(self, lastMeasure=None, m={}):
        m['best'] = self._bestSol[1]
        if lastMeasure is not None and 'best' in lastMeasure:
            m['valueIncrease'] = self._bestSol[1] - lastMeasure['best']  # doesn't work
        else:
            m['valueIncrease'] = self._bestSol[1]  # doesn't work
        return super(BruteForce, self).measure(lastMeasure=lastMeasure, m=m)

    def step(self):
        """
        Visualization data exchange protocol:
        Json encoded object having 3 fields: `current` `best` and `done`
        The two first holds an object with the fields `solution` (that contains
        the actual solution) and `evaluation` (that contains the evaluation for
        this solution).
        The latter is a boolean indicating if the process is terminated.
        """
        # get the next possible solution. If the generator has finished
        # (i.e.: all search space has been explored), then raise the best
        # solution found.
        try:
            solution = self._solGenerator.next()
        except StopIteration:
            self._log(
                'Done. Best overall: %s [%.3f]'
                % (str(self._bestSol[0]), self._bestSol[1]), force=True,
                level=4)
            print "Bruteforce optimizing task performed in %.3fs" \
                % (time.time() - self._start_t)
            raise OptimizationSolution(*self._bestSol)

        # if there is a solution to evaluate, do it.
        evaluation = self._problem.evaluate(solution)
        # if the evaluated solution is better than the best found
        # up to this point, save it.
        if self._bestSol is None or self._problem.isBetter(
                evaluation, self._bestSol[1]):
            self._log(
                '>>> [%.3f] %s is better!' % (evaluation, str(solution)),
                timeout=0.01, level=3)
            self._bestSol = (solution, evaluation)

        # a bit of logging
        self._log(
            'Evaluation: %s [%.3f]' % (str(solution), evaluation), level=1)
        self._viz({
            'current': {'solution': solution, 'evaluation': evaluation},
            'best': {'solution': self._bestSol[0],
                     'evaluation': self._bestSol[1]}
        })
