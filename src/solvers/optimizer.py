# -*- coding: utf8 -*-

from __future__ import unicode_literals

from baseSolver import BaseSolver


class Optimizer(BaseSolver):
    """Any optimizer should inherit from this base class"""
    def __init__(self, name, problem):
        super(Optimizer, self).__init__(
            solverType='optimizer', name=name,
            problem=problem)
