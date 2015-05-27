# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId
from string import Template

from tornado import gen

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
            'name': False,
            'parameters': True,
            'implementation': True,
            'visualization': True,
            'dataset': False
        }

    def _computeName(self, problem):
        """
        Computes the name of this problem based on its implementation and
        parameters.
        """
        template = Template("problem $implem, $params")
        res = template.substitute(
            implem=problem['implementation'],
            params=', '.join(
                '='.join(p) for p in problem['parameters'].iteritems()))
        if 'dataset' in problem and problem['dataset']:
            res += ' ; dataset=' + problem['dataset']
        problem['_generatedName'] = True
        return res

    @gen.coroutine
    def getById(self, _id, fields=None):
        """
        Return a future over the document specific to this id. call yield over
        the future to resolve it.
        `fields` allow to select which field will be returned, everything is
        returned by default.
        """
        # retrieve the problem
        if fields is None:
            problem = yield self._collection.find_one({'_id': ObjectId(_id)})
        else:
            problem = yield self._collection.find_one(
                {'_id': ObjectId(_id)},
                self.validate({f: True for f in fields}, strict=False))
        if problem is None:
            raise gen.Return(None)

        if (not 'name' in problem or not problem['name']) and fields is None:
            problem['name'] = self._computeName(problem)

        # returns the problem
        raise gen.Return(problem)

    @gen.coroutine
    def getByIds(self, ids, fields=None):
        """
        Get a list of documents that are matching the given ids.
        Returns a future object. Yield the returned future to get the
        actual result.
        """
        query = {
            '_id': {
                '$in': [ObjectId(_id) if not isinstance(_id, ObjectId) else _id
                        for _id in ids]}
        }
        if fields is not None:
            cur = self._collection.find(
                query, self.validate({f: True for f in fields}))
        else:
            cur = self._collection.find(query)
        problems = []
        for problem in (yield cursor.to_list(length=None)):
            if (not 'name' in problem or not problem['name']) \
                    and fields is None:
                problem['name'] = self._computeName(problem)
            problems.append(problem)

        raise gen.Return(problems)

    @gen.coroutine
    def getAll(self, page=0, perPage=0, orderBy=None):
        """
        Returns all documents available in this collection.
        * page:int is the page number (default is 0)
        * perPage:int is the number of element per page (default displays all
          elements)
        * orderBy: dict allow to select on which field to perform the ordering
        Returns a future. Call `yield` operator to resolve it.
        """
        if orderBy is None:
            cursor = self._collection.find({})
        else:
            cursor = self._collection.find({'$query': {}, '$orderby': orderBy})
        if page > 0 and perPage > 0:
            cursor.skip((page - 1) * perPage).limit(perPage)

        problems = []
        for problem in (yield cursor.to_list(length=None)):
            if not 'name' in problem or not problem['name']:
                problem['name'] = self._computeName(problem)
            problems.append(problem)

        raise gen.Return(problems)
