# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId

from baseService import Service

"""
# solverTemplates collection.
Solver descriptors, they hold all the data that is specific to a solver and
needed to instanciate one, except user-configurable parameters.
Schema:
    * _id:ObjectId, id of the solver template
    * type:string, type of the solver, either "clustering", "classification"
      or "optimizer".
    * basename:string, unique name for this template
    * parameters:dict, associates the name of the user-configurable parameters
      to the type of the data. The type determines the control needed to let
      the user pick a value (e.g.: int, uint, float, ufloat, etc...)
    * implementation:string, name of the python class that contains the actual
      implementation for this solver. The class should follow the interface
      defined for this type of solver
    * visualization:string, the javascript file that follow the interface for a
      solver view, i.e.: it should listen to a websocket where the
      implementation of the solver will push data whenever an update is
      available, and draw the representation of the evolution of the algorithm.
"""


class SolverTemplatesService(Service):
    def __init__(self, db):
        super(SolverTemplatesService, self).__init__(db, 'solverTemplates')

    def schema(self):
        return {
            'type': True,
            'basename': True,
            'parameters': True,
            'implementation': True,
            'visualization': True
        }
