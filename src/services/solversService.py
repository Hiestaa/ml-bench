# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId

from tornado import gen

from baseService import Service
from tools import model

"""
# solvers collection
Stores the data related to an instanciated / configured solver
(i.e.: ready to be run)
Schema:
    * _id:ObjectId, id of the solver instance
    * type:string, type of the solver, either "clustering", "classification"
      or "optimizer".
    * name:string, unique full display name for this instance.
      Can be user-configured or auto-generated by appending to the basename the
      name and value of each parameter.
    * parameters:dict, associates the parameter value to its corresponding
      name.
    * implementation:string, name of the python class that contains the actual
      implementation for this solver. The class should follow the interface
      defined for this type of solver
    * visualization:string, the javascript file that follow the interface for a
      solver view, i.e.: it should listen to a websocket where the
      implementation of the solver will push data whenever an update is
      available, and draw the representation of the evolution of the algorithm.
    * problemId:ObjectId, id of the problem this algorithm intends to solve.
      See: `problemsService.py`.
"""


class SolversService(Service):
    def __init__(self, db):
        super(SolversService, self).__init__(db, 'solvers')

    def schema(self):
        return {
            'type': True,
            'name': True,
            'parameters': True,
            'problemId': True,
            'implementation': True,
            'visualization': True
        }

    def insert(self, **kwargs):
        """
        Insert a new document entry into the "solvers" collection.
        The keywords arguments should match the schema defined for this
        entry. If the optional `_id` keyword argument is given, the `_id` of
        the document will not be automatically generated.
        Note: the given `_id` (if any) will be converted to an ObjectId and has
        to be a compatible string.
        Note bis: the given"problemId" should be ObjectId compatible strings
        as well.
        """
        logging.debug("Saving new entry: %s" % ", ".join(
            reduce(lambda name, value: "%s - %s" % (name, value),
                   kwargs.iteritems())))
        post = self.schema()
        for name, value in kwargs.iteritems():
            post[name] = value
            if name == 'problemId':
                post[name] = ObjectId(post[name])
        if '_id' in post:
            if not isinstance(post['_id'], ObjectId):
                post['_id'] = ObjectId(post['_id'])
        return self._collection.insert(self.validate(post))

    @gen.coroutine
    def getById(self, _id, fields=None):
        """
        Return a future over the document specific to this id. call yield over
        the future to resolve it.
        `fields` allow to select which field will be returned, everything is
        returned by default.
        This will use the problemService to add a `problem` field
        that contains the problem corresponding to the problem linked by the
        `problemId` field.
        """
        # retrieve the solver
        if fields is None:
            solver = yield self._collection.find_one({'_id': _id})
        else:
            solver = yield self._collection.find_one(
                {'_id': _id},
                self.validate({f: True for f in fields}, strict=False))
        # retrieve the linked problem
        problem = yield model.getService('problems').getById(
            solver['problemId'])

        # create the `problem` entry in the solver.
        solver['problem'] = problem

        # returns the solver
        raise gen.Return(solver)

    def deleteByProblemId(self, problemId):
        """
        Removes all solution related to the given problem id.
        * problemId:string, ObjectId compatible.
        Returns a future that should be yielded to resolve it.
        """
        return self._collection.remove({'problemId': ObjectId(problemId)})
