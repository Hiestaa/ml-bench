# -*- coding: utf8 -*-

from __future__ import unicode_literals

from baseSolver import BaseSolver


class Classifier(BaseSolver):
    """Any Classifier should inherit from this base class"""
    def __init__(self, name, problem):
        super(Clusterer, self).__init__(
            solverType='classifier', name=name,
            problem=problem)
