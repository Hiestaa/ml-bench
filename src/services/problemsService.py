# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId

from baseService import Service

"""
# problems collection
Stores data related to a problem that can be used as a support to benchmark the
instanciated solvers.
Schema:
    * _id:ObjectId, id of the problem
    * types:list<string>, the types of solvers that can be used to solve this
      problem. A problem may indeed be presented in many ways, for instance a
      clustering problem can be solver by an optimizer.
      This list should be derived from the list of interfaces the python class
      of this problem is implementing.
    * name:string, the name of this problem
    * parameters:dict, associates the name of a parameter to a value of any
      type. Those parameters will be given to the constructor of the problem
      class as keyword arguments.
    * implementation:string, the name of the python class that contains the
      code of this problem. This class should implement the interfaces
      described by the `types` entry.
    * visualization:string, the name of the file that contains the javascript
      code allowing to visualize the evolution of the problem getting solver as
      the algorithm is running.
      This code should follow the interface for a "problem view",
      i.e.: listen to a websocket for an update of the computed problem
      solution and display it visually.
    * dataset:name, link to a dataset, if relevant. Some problems
      (e.g.: finding the optimum of a function) may not require any data to be
      solved. Others (e.g.: data clustering / classification) will do.
      If a dataset is required, this entry should contain the name of a python
      class that implements the "DataContainer" interface, which has a function
      that loads a file and fo whatever is required to vectorize the raw data.
"""


class ProblemsService(Service):
    def __init__(self, db):
        super(ProblemsService, self).__init__(db, 'problems')

    def schema(self):
        return {
            'types': True,
            'name': True,
            'parameters': True,
            'implementation': True,
            'visualization': True,
            'dataset': False
        }
