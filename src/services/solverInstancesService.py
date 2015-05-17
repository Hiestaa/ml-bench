# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId

from baseService import Service

"""
# solverInstances collection
Stores the data related to an instanciated / configured solver
(i.e.: ready to be run)
Schema:
    * _id:ObjectId, id of the solver instance
    * templateId:ObjectId, id of the related solver template. Needed to get an
      access to the solver's implementation & visualization code, type, etc...
      See: `solverTemplatesService.py`
    * fullname:string, unique full display name for this instance.
      Can be user-configured or auto-generated by appending to the basename the
      name and value of each parameter.
    * parameters:dict, associates the user-defined parameter value to each
      parameter name.
    * problemId:ObjectId, id of the problem this algorithm intends to solve.
      See: `problemsService.py`.
"""


class SolverInstancesService(Service):
    def __init__(self, db):
        super(SolverInstancesService, self).__init__(db, 'solverInstances')

    def schema(self):
        return {
            'templateId': True,
            'fullName': True,
            'parameters': True,
            'problemId': True,
        }

    def insert(self, **kwargs):
        """
        Insert a new document entry into the "solverInstances" collection.
        The keywords arguments should match the schema defined for this
        entry. If the optional `_id` keyword argument is given, the `_id` of
        the document will not be automatically generated.
        Note: the given `_id` (if any) will be converted to an ObjectId and has
        to be a compatible string.
        Note bis: the given "templateId" and "problemId" should be ObjectId
        compatible strings as well.
        """
        logging.debug("Saving new entry: %s" % ", ".join(
            reduce(lambda (name, value): "%s - %s" % (name, value),
                   kwargs.iteritems())))
        post = self.schema()
        for name, value in kwargs.iteritems():
            post[name] = value
            if name == 'templateId' or name == 'problemId':
                post[name] = ObjectId(post[name])
        if '_id' in post:
            if not isinstance(post['_id'], ObjectId):
                post['_id'] = ObjectId(post['_id'])
        return self._collection.insert(self.validate(post))
