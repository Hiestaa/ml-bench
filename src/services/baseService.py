# -*- coding: utf8 -*-
from __future__ import unicode_literals

from pprint import pformat
import logging

from bson.objectid import ObjectId

from conf import Conf


class ModelException(Exception):
    pass


class Service(object):
    """
    Base class of any service, provide some abstraction of common functions
    Note: all the function provided by the service are wrapping motor operation
    meaning that they return a future - call 'yield' in a coroutine
    to resolve the future and get the actual result.
    """
    def __init__(self, db, collection):
        super(Service, self).__init__()
        self._db = db
        self._collection = self._db[collection]

    def schema(self):
        """
        Note: override this function to enable schema-validation
        """
        return {}

    def validate(self, query, strict=True):
        """
        Validate the query to ensure it matches the defined schema.
        If the schema method is overrode to return a valid schema
        object (a dict where keys are expected document fields, and values
        are set to True if the field is required, False otherwise),
        this function will check the query and ensure that there is no
        unexpected or missing required keys (by raising a ModelException).
        Returns the validated query.
        If strict is set to False, the required keys won't be tested. This
        can be useful to validate an update query, ensuring that the field
        updated is not out of the schema.
        """
        schema = self.schema()
        schema_keys = set(schema)
        # if there is no keys in the schema, exit
        if len(schema_keys) == 0:
            return query
        required_schema_keys = set([k for k in schema_keys if schema[k]])

        query_keys = set(query.keys())

        # no unexpected keys: all the keys of the queries exist
        # in the schema. An exception, the key _id, can be specified
        # even
        union = schema_keys | query_keys
        if len(union) > len(schema_keys):
            diff = query_keys - schema_keys
            if len(diff) > 1 or not '_id' in diff:
                raise ModelException(
                    "The keys: %s are unexpected in the validated query."
                    % str(query_keys - schema_keys))

        if not strict:
            return query

        # all required keys are here
        intersect = required_schema_keys & query_keys
        if len(intersect) < len(required_schema_keys):
            raise ModelException(
                "The required keys: %s are missing in the validated query"
                % str(required_schema_keys - query_keys))

        return query

    def insert(self, **kwargs):
        """
        Insert a new document entry into the collection of this service.
        The keywords arguments should match the schema defined for this
        entry. If the optional `_id` keyword argument is given, the `_id` of
        the document will not be automatically generated.
        Note: the given `_id` (if any) will be converted to an ObjectId and has
        to be a compatible string.
        Returns a future that contains the `_id` of the inserted field
        """
        logging.debug("Saving new entry: %s" % ", ".join(
            reduce(lambda name, value: "%s - %s" % (name, value),
                   kwargs.iteritems())))
        post = self.schema()
        for name, value in kwargs.iteritems():
            post[name] = value
        if '_id' in post:
            if not isinstance(post['_id'], ObjectId):
                post['_id'] = ObjectId(post['_id'])
        return self._collection.insert(self.validate(post))

    def getById(self, _id, fields=None):
        """
        Return a document specific to this id
        _id is the _id of the document
        fields is the list of fields to be returned (all by default)
        """
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        if fields is None:
            return self._collection.find_one({'_id': _id})
        projection = {f: True for f in fields}
        return self._collection.find_one({'_id': _id}, self.validate(
            projection, strict=False))

    def getByIds(self, ids, fields=None):
        """
        Get a list of documents that are matching the given ids.
        Returns a cursor wrapped around a future. Call
        `yield cursor.to_list(length=None)` to get the actual returned data.
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
        return cur

    def getOverallCount(self):
        return self._collection.count()

    def deleteAll(self):
        """
        Warning: will delete ALL the documents in this collection
        """
        return self._collection.remove({})

    def deleteById(self, _id):
        logging.info("removing by id: %s" % _id)
        return self._collection.remove({'_id': ObjectId(_id)})

    def getAll(self, page=0, perPage=0, orderBy=None):
        """
        Returns all documents available in this collection.
        * page:int is the page number (default is 0)
        * perPage:int is the number of element per page (default displays all
          elements)
        * orderBy: dict allow to select on which field to perform the ordering
        Returns the cursor over the list of documents wrapped around a Future.
        Call `yield cursor.to_list(length=None)` to get the actual list of docs
        """
        if orderBy is None:
            cursor = self._collection.find({})
        else:
            cursor = self._collection.find({'$query': {}, '$orderby': orderBy})
        if page > 0 and perPage > 0:
            cursor.skip((page - 1) * perPage).limit(perPage)
        return cursor

    def set(self, _id, field, value=None):
        """
        Set the given field(s) to the given value(s).
        If _id is a list, it will be used as a list of ids.
        If field is a dict, the association between field name and value set
        is expected. In this case, value will be ignored.
        All documents matching these ids will be modified
        """
        select = {'_id': _id}
        if isinstance(_id, list):
            select['_id'] = {'$in': [ObjectId(i) for i in _id]}
        else:
            select['_id'] = ObjectId(_id)
        if isinstance(field, dict):
            update = field
        else:
            update = {field: value}
        return self._collection.update(
            select,
            {'$set': self.validate(update, strict=False)},
            multi=True
        )
