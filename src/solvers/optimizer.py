# -*- coding: utf8 -*-

from __future__ import unicode_literals

from baseSolver import BaseSolver


class Optimizer(BaseSolver):
    """Any optimizer should inherit from this base class"""
    def __init__(self, fullName, problem, parameters={}):
        super(Optimizer, self).__init__(
            solverType='optimizer', fullName=fullName,
            problem=problem, parameters=parameters)

