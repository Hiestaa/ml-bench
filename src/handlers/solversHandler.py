# -*- coding: utf8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, HTTPError
from tornado import gen

import logging
import json
import inspect
import os
import pkgutil

from tools import model
from tools.utils import lcFirst, ucFirst, genModules
from solvers.optimizer import Optimizer
from solvers.clusterer import Clusterer
from solvers.classifier import Classifier
from conf import Conf
from mlbExceptions import SolverException


class SolversHandler(RequestHandler):
    """Handle API requests for solver-related data"""
    @gen.coroutine
    def getSolvers(self):
        """
        Route: `GET /api/solvers/list`
        Returns the list of existing solver objects
        TODO: Add pagination system
        """
        def desobjectidfy(solver):
            solver['problemId'] = str(solver['problemId'])
            return solver

        cursor = model.getService('solvers').getAll(
            orderBy={'implementation': 1, 'name': 1})

        solvers = [
            desobjectidfy(solver) for solver in
            (yield cursor.to_list(length=None))]

        self.write(json.dumps(solvers))

    @gen.coroutine
    def deleteSolverById(self):
        """
        Route: `DELETE /api/solvers/byId`
        Remove the solver given by id.
        The argument `_id` is required.
        """
        _id = self.get_argument('_id')
        data = yield model.getService('solvers').deleteById(_id)
        self.write(json.dumps(data))

    def getSolverClasses(self):
        """
        Route: `GET /api/solvers/implementations`
        Return the list available solver classes, indexed by types.
        This writes back to the client an object with the following structure:
        `{<solverType>: {<className>: {
            'description': <description>,
            'parameters': [<parameter names to be defined by the class>]
        }}`
        """
        result = {
            'optimizer': {},
            'clusterer': {},
            'classifier': {}
        }

        for moduleName in genModules(['solvers']):
            classObj = {}
            # for each module, get the actual implementation class
            implemModule = __import__(
                'solvers.%s' % moduleName, fromlist=[ucFirst(moduleName)])
            implemClass = getattr(implemModule, ucFirst(moduleName))

            # now find the arguments of the constructor, remove 'self' and
            # 'name' which are not user-configurable parameters specific to
            # this solver.
            argspec = inspect.getargspec(implemClass.__init__)
            argspec.args.remove('self')
            argspec.args.remove('name')
            argspec.args.remove('problem')
            if argspec.defaults:
                classObj['parameters'] = dict(
                    zip(argspec.args[-len(argspec.defaults):],
                        argspec.defaults))
            else:
                classObj['parameters'] = {}

            # find the documentation of this object
            classObj['description'] = inspect.cleandoc(
                inspect.getdoc(implemClass))

            # now find inheritance tree to know where this class should be
            # saved.
            implemClasses = inspect.getmro(implemClass)
            if Optimizer in implemClasses and moduleName != 'optimizer':
                result['optimizer'][ucFirst(moduleName)] = classObj
            if Clusterer in implemClasses and moduleName != 'clusterer':
                result['clusterer'][ucFirst(moduleName)] = classObj
            if Classifier in implemClasses and moduleName != 'classifier':
                result['classifier'][ucFirst(moduleName)] = classObj

        self.write(json.dumps(result))

    @gen.coroutine
    def saveSolver(self):
        """
        Route: `POST: /api/solvers/save`
        Save a new or update an existing solver.
        The following parameters are expected:
        * name:string, name of this solver
        * parameters:json-encoded dict, association between parameters'
          name and value
        * implementation:string, name of the related solver class
        * visualization:string (optional), name of the script that contains the
          visualization javascript code.
        * problem:string, id of the problem this solver is designed to solve
        * _id:string (optional), the _id of the document to update. If not
          provided, an new document will be inserted.
        Writes back the whole inserted or updated document
        """
        name = self.get_argument('name')
        parameters = json.loads(self.get_argument('parameters'))
        implementation = self.get_argument('implementation')
        visualization = self.get_argument('visualization', default=None)
        problem = self.get_argument('problem')
        _id = self.get_argument('_id', default=None)

        # retrieve the type of this implementation
        # TODO: make sure that the class 'implementation' exists
        implemModule = __import__(
            'solvers.%s' % lcFirst(implementation),
            fromlist=[implementation])
        implemClasses = inspect.getmro(getattr(implemModule, implementation))

        solverType = None
        if Optimizer in implemClasses:
            solverType = 'optimizer'
        if Clusterer in implemClasses:
            solverType = 'clusterer'
        if Classifier in implemClasses:
            solverType = 'classifier'
        # makes sure the implementation implements one of the solver interface
        if solverType is None:
            raise SolverException(
                solverType, name, parameters,
                "The given implementation (%s) does not implement any solver \
type interface." % (implementation))

        # check that the given visualization exist
        if visualization:
            # this will raise an exception if the field does not exist
            with open(os.path.join(*(
                    os.path.split(Conf['scriptFolders']['solverViews']) +
                    (visualization,)))):
                pass

        problemObj = yield model.getService('problems').getById(
            problem, fields=['_id'])
        if not problemObj:
            raise SolverException(
                solverType, name, parameters,
                "The given problem (%s) does not exist!" % (problem))

        # perform the actual insert/update
        data = {
            'type': solverType,
            'name': name,
            'parameters': parameters,
            'visualization': visualization,
            'problemId': problem,
            'implementation': implementation
        }
        if _id is None:
            _id = yield model.getService('solvers').insert(**data)
        else:
            yield model.getService('solvers').set(_id, data)
        data['_id'] = str(_id)
        self.write(json.dumps(data))

    def get(self, action):
        actions = {
            'implementations': self.getSolverClasses,
            'list': self.getSolvers
        }
        if action in actions:
            return actions[action]()
        raise HTTPError(404, 'Not Found')

    def post(self, action):
        actions = {
            'save': self.saveSolver
        }
        if action in actions:
            return actions[action]()
        raise HTTPError(404, 'Not Found')

    def delete(self, action):
        actions = {
            'byId': self.deleteSolverById
        }
        if action in actions:
            return actions[action]()
        raise HTTPError(404, 'Not Found')
