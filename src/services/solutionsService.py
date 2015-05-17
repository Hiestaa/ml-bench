# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging
from bson.objectid import ObjectId

from baseService import Service

"""
# solutions collection
Describes a solution computed by a solver to a problem, and contains
stores performed as the algorithm was running and on the final solution
allowing to draw chart and tables showing the relevance of each solution.
Schema:
    * _id:ObjectId, id of the solution
    * problemId:ObjectId, id of the problem this solution has been computed for
    * solverId:ObjectId, id of the instance of solver that was used to compute
      this solution.
    * solution:list<float> this actual solution found as vectorized data.
      Each problem should be able to interpret this vector and transform is as
      a semantic, human-understandable solution.
    * ... measurements ...
"""


class SolutionsService(Service):
    def __init__(self, db):
        super(SolutionsService, self).__init__(db, 'solutions')

    def schema(self):
        return {
            'problemId': True,
            'solverId': True,
            'solution': True,
        }

    def insert(self, **kwargs):
        """
        Insert a new document entry into the "solutions" collection.
        The keywords arguments should match the schema defined for this
        entry. If the optional `_id` keyword argument is given, the `_id` of
        the document will not be automatically generated.
        Note: the given `_id` (if any) will be converted to an ObjectId and has
        to be a compatible string.
        Note bis: the given "problemId" and "solverId" should be ObjectId
        compatible strings as well.
        """
        logging.debug("Saving new entry: %s" % ", ".join(
            reduce(lambda (name, value): "%s - %s" % (name, value),
                   kwargs.iteritems())))
        post = self.schema()
        for name, value in kwargs.iteritems():
            post[name] = value
            if name == 'problemId' or name == 'solverId':
                post[name] = ObjectId(post[name])
        if '_id' in post:
            if not isinstance(post['_id'], ObjectId):
                post['_id'] = ObjectId(post['_id'])
        return self._collection.insert(self.validate(post))
