# -*- coding: utf8 -*-

from __future__ import unicode_literals


class MLBenchException(Exception):
    """Base exception for all exceptions of this project"""
    pass


class SolverException(MLBenchException):
    """
    Exception specific to a solver."""
    def __init__(self, solverType, fullName, parameters, *args, **kwargs):
        super(SolverException, self).__init__(*args, **kwargs)
        self._solverType = solverType
        self._fullName = fullName
        self._parameters = parameters


class ProblemException(MLBenchException):
    """
    Exception specific to a problem.
    """
    def __init__(self, problemTypes, name, parameters, *args, **kwargs):
        super(ProblemException, self).__init__(*args, **kwargs)
        self._problemTypes = problemTypes
        self._name = name
        self._parameters = parameters
