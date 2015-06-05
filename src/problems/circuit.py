# -*- coding: utf8 -*-

from __future__ import unicode_literals

from optimization import Optimization
import numpy as np
import math


def cityblock(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def euclidean(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


class Circuit(Optimization):
    """
    This optimization problem is an electronic circuit where each
    component is placed on a grid of size `N*M`. The component at
    position `x, y` is connected to the ones at the positions `x + 1, y`,
    `x, y + 1`, `x - 1, y` and `x, y - 1`. During problem initialization,
    the order of the components are shuffled, the goal of the problem is
    to find the configuration in which the connection between two components
    is the shortest.
    * `width`: the number of components on the first dimension of the circuit
    * `height`: the number of components on the second dimension of the circuit
    * `distance`: the distance function to use. Accepted values are:
      'euclidean' (the default) and 'cityblock'. Any other value will be
      ignored and 'euclidean' will be used instead.
    """
    def __init__(self, name, dataset, width=5, height=5, distance='euclidean'):
        super(Circuit, self).__init__(
            name=name, dataset=dataset, width=width, height=height,
            distance=distance)
        self._width = int(width)
        self._height = int(height)
        self._distance = cityblock if distance == 'cityblock' \
            else euclidean

    def getScope(self):
        """
        Returns an array, where each variable of the optimization problem
        is associated with its range and type as a tuple (type, min, max).
        (variables have no name for the optimizer, only an index)
        In that case, the type is an integer and the range is the size
        of the circuit (for a 5 * 5 circuit, each component can be placed on
        the grid at position between 0 and 24.)
        """
        return [
            (int, 0, (self._width) * (self._height) - 1)
            for i in xrange(self._width * self._height)
        ]

    def isBetter(self, evaluation1, evaluation2):
        """
        An evaluation is better than another if it is smaller.
        """
        return evaluation1 < evaluation2

    def evaluate(self, solution):
        """
        Evaluate the given solution.
        The solution is a single-dimensional array, where the position of the
        component (x, y) can be found at solution[x + y * width].
        """
        # contains duplicates
        if len(set([int(x) for x in solution])) < len(solution):
            return (self._width * self._height * 25) ** 2

        # map onto a grid
        def componentsPosition(x, y):
            """
            Returns the position of the component (x, y) as defined in the
            given solution
            """
            return int(solution[x + y * self._width])

        def pos2Coord(pos):
            """
            Returns the actual coordinates of the component that is located
            at position `pos`.
            This convert the virtual 1D grid into the coordinates in the
            virtual 2D circuit to allow distance computation.
            """
            # transform a solution value into a 2 components position
            return (pos % self._width * 5, pos / self._height * 5)

        def computeCnxLen(compo):
            """
            Compute the length of the connexion between the given
            component and its neighbors (right and down) using the
            distribution given by the solution.
            """
            # compo = (row, col)
            length = 0
            if compo[0] + 1 < self._width:
                length += self._distance(
                    pos2Coord(componentsPosition(compo[0], compo[1])),
                    pos2Coord(componentsPosition(compo[0] + 1, compo[1])))
            if compo[1] + 1 < self._height:
                length += self._distance(
                    pos2Coord(componentsPosition(compo[0], compo[1])),
                    pos2Coord(componentsPosition(compo[0], compo[1] + 1)))
            return length
            print res, solution

        return sum(computeCnxLen((x, y)) for x in xrange(self._width - 1)
                   for y in xrange(self._height - 1))
