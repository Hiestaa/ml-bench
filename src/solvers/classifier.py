# -*- coding: utf8 -*-

from __future__ import unicode_literals

from baseSolver import BaseSolver


class Classifier(BaseSolver):
    """Any Classifier should inherit from this base class"""
    def __init__(self, fullName, problem, parameters={}):
        super(Clusterer, self).__init__(
            solverType='classifier', fullName=fullName,
            problem=problem, parameters=parameters)
