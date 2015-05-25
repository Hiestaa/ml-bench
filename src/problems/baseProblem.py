# -*- coding: utf8 -*-

from __future__ import unicode_literals

from mlbExceptions import ProblemException

"""
Recepie to create a new problem.
* Select your problem type(s). Create the class of your problem, and
  inherit from `Optimization`, `Clustering`, `Classification` or any
  combination of them.
* Implement the `__init__` function. It must take at least the
  parameters `name` and and `dataset` (it may or may not use it).
  If may use any other keyword parameters that will be considered as
  user-defined problem-related parameters. These arguments must be provided
  with a default value.
  The `super([...], self).__init__` function should be called with all these
  argument's values
* Implement the functions defined in the parent class, or classes.
"""


class BaseProblem(object):
    """
    Represents any problem hat can be solved by a solver.
    Any problem class should inherit from this one (actually, from
    one or more of the classes that inherint from this one)
    The purpose of a Problem class is to describe a problem using mathematical
    vectors, optionally using a dataset.
    Note: any problem class should lie in a module (file) that has the
    **exact same name** as the defined class, **first letter lowercased**.
    Note 2: the documentation of sub-classes will be used as description
    provided to the user when creating an instance of this problem
    (i.e.: setting the parameters using the front-end UI)
    """
    def __init__(self, problemTypes, name, dataset=None, **kwargs):
        """
        Initialize a new problem.
        * problemType:string the type of this problem, either "optimization",
          "clustering" or "classification".
        * name:string, name of this problem, for identification purpose
        * dataset:DataContainer, a class that is able to read data from a file,
          pre-process the data (if needed) and convert them into vectors.
        * parameters:dict, user-defined parameters relative to this problem
        """
        super(BaseProblem, self).__init__()
        for problemType in problemTypes:
            if not problemType in ['optimization',
                                   'clustering',
                                   'classification']:
                raise ProblemException(
                    problemTypes, name, kwargs,
                    "Invalid problem type: %s" % problemType)
        self._problemTypes = problemTypes
        self._name = name
        self._dataset = dataset
