# -*- coding: utf8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, HTTPError, authenticated
from tornado import gen

import logging
import json
import inspect
import os
import pkgutil

from tools import model
from tools.utils import lcFirst, ucFirst, genModules
from problems.optimization import Optimization
from conf import Conf
from mlbExceptions import ProblemException


class ProblemsHandler(RequestHandler):
    """Handle API requests for problems-related data"""
    @gen.coroutine
    def getProblems(self):
        """
        Route: `GET /api/problems/list`
        Returns the list of existing problem objects
        TODO: Add pagination system
        """
        cursor = model.getService('problems').getAll(
            orderBy={'implementation': 1, 'name': 1})

        problems = [
            problem for problem in (yield cursor.to_list(length=None))]

        self.write(json.dumps(problems))

    def getProblemClasses(self):
        """
        Route: `GET /api/problems/implementations`
        Return the list available problem classes, indexed by types.
        This writes back to the client an object with the following structure:
        `{<problemType>: {<className>: {
            'description': <description>,
            'parameters': [<parameter names to be defined by the user>]
        }}`
        """
        result = {
            'optimization': {},
            'clustering': {},
            'classification': {}
        }

        for moduleName in genModules(['problems']):
            classObj = {}
            # for each module, get the actual implementation class
            implemModule = __import__(
                'problems.%s' % moduleName, fromlist=[ucFirst(moduleName)])
            implemClass = getattr(implemModule, ucFirst(moduleName))

            # now find the arguments of the constructor, remove 'self' and
            # 'name' which are not user-configurable parameters specific to
            # this problem.
            argspec = inspect.getargspec(implemClass.__init__)
            argspec.args.remove('self')
            argspec.args.remove('name')
            if 'dataset' in argspec.args:
                argspec.args.remove('dataset')
            if argspec.defaults:
                classObj['parameters'] = dict(
                    zip(argspec.args[-len(argspec.defaults):],
                        argspec.defaults))
            # find the documentation of this object
            classObj['description'] = inspect.cleandoc(
                inspect.getdoc(implemClass))

            # now find inheritance tree to know where this class should be
            # saved.
            implemClasses = inspect.getmro(implemClass)
            if Optimization in implemClasses and moduleName != 'optimization':
                result['optimization'][ucFirst(moduleName)] = classObj
            # todo: fill in the 'clustering' and 'classification' fields

        self.write(json.dumps(result))

    @gen.coroutine
    def saveProblem(self):
        """
        Route: `POST: /api/problems/save`
        Save a new or update an existing problem.
        The following parameters are expected:
        * name:string, name of this problem
        * parameters:json-encoded dict, association between parameters'
          name and value
        * implementation:string, name of the related problem class
        * visualization:string (optional), name of the script that contains the
          visualization javascript code.
        * dataset:string (optional), name of the related dataset, if any
        * _id:string (optional), the _id of the document to update. If not
          provided, an new document will be inserted.
        Writes back the whole inserted or updated document
        """
        name = self.get_argument('name')
        parameters = json.loads(self.get_argument('parameters'))
        implementation = self.get_argument('implementation')
        visualization = self.get_argument('visualization', default=None)
        dataset = self.get_argument('dataset', default=None)
        _id = self.get_argument('_id', default=None)

        # retrieve the type of this implementation
        # TODO: make sure that the class 'implementation' exists
        implemModule = __import__(
            'problems.%s' % lcFirst(implementation),
            fromlist=[implementation])
        implemClasses = inspect.getmro(getattr(implemModule, implementation))

        problemTypes = []
        if Optimization in implemClasses:
            problemTypes.append('optimization')
        # TODO: check if Clustering or Classification is in the implenClasses
        #       list
        # makes sure the implementation implements at least one problem type
        # interface
        if len(problemTypes) == 0:
            raise ProblemException(
                problemTypes, name, parameters,
                "The given implementation (%s) does not implement any problem \
type interface." % (implementation))

        # check that the given visualization exist
        if visualization:
            # this will raise an exception if the field does not exist
            with open(os.path.join(*(
                    os.path.split(Conf['scriptFolders']['problemViews']) +
                    (visualization,)))):
                pass

        # todo: check that the given `dataset` exists and is a subclass of
        # `DataContainer`.

        # perform the actual insert/update
        data = {
            'types': problemTypes,
            'name': name,
            'parameters': parameters,
            'visualization': visualization,
            'dataset': dataset,
            'implementation': implementation
        }
        if _id is None:
            _id = yield model.getService('problems').insert(**data)
        else:
            yield model.getService('problems').set(_id, data)
        data['_id'] = str(_id)
        self.write(json.dumps(data))

    def get(self, action):
        actions = {
            'implementations': self.getProblemClasses,
            'list': self.getProblems
        }
        if action in actions:
            return actions[action]()
        raise HTTPError(404, 'Not Found')

    def post(self, action):
        actions = {
            'save': self.saveProblem
        }
        if action in actions:
            return actions[action]()
        raise HTTPError(404, 'Not Found')
