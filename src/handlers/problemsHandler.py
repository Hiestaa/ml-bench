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
from tools.utils import lcFirst, ucFirst
from problems.optimization import Optimization


class ProblemsHandler(RequestHandler):
    """Handle API requests for problems-related data"""
    def getProblemClasses(self):
        """
        Route: `GET /api/problems/implementations`
        Return the list available problem types, indexed by types.
        This writes back to the client an object with the following structure:
        `{<problemType>: {<className>: {
            'description': <description>,
            'parameters': [<parameter names to be defined by the user>]
        }}`
        """
        def genModules(pkgs):
            """
            **SHOULD** recursively yield all the modules in the given package.
            TO BE TESTED!
            """
            logging.info("Listing modules in package: %s" % str(pkgs))
            next_level = []
            for (module_loader, name, is_pkg) in pkgutil.iter_modules(
                    path=pkgs):
                if is_pkg:
                    next_level.append(name)
                else:
                    logging.info(">> Found submodule: %s" % name)
                    yield name
            for name in genModules(next_level):
                yield name

        result = {
            'optimization': {},
            'clustering': {},
            'classification': {}
        }

        for name in genModules(['problems']):
            classObj = {}
            # for each module, get the actual implementation class
            implemModule = __import__(
                'problems.%s' % name, fromlist=[ucFirst(name)])
            implemClass = getattr(implemModule, ucFirst(name))

            # now find the arguments of the constructor, remove 'self' and
            # 'name' which are not user-configurable parameters specific to
            # this problem.
            argspec = inspect.getargspec(implemClass.__init__)
            argspec.args.remove('self')
            argspec.args.remove('name')
            classObj['parameters'] = argspec.args

            # find the documentation of this object
            classObj['description'] = inspect.cleandoc(
                inspect.getdoc(implemClass))

            # now find inheritance tree to know where this class should be
            # saved.
            implemClasses = inspect.getmro(implemClass)
            if Optimization in implemClasses:
                result['optimization'][name] = classObj
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
        Writes back the id of the updated or inserted document.
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
        if visualization is not None:
            # this will raise an exception if the field does not exist
            with open(os.path.join(*(
                    os.path.split(Conf['scriptFolders']['problemViews']) +
                    visualization))):
                pass

        # perform the actual insert/update
        if _id is None:
            _id = yield model.getService('problems').insert(
                types=problemTypes, name=name, parameters=parameters,
                implementation=implementation, visualization=visualization,
                dataset=dataset)
        else:
            yield model.getService('problems').set(_id, {
                'types': problemTypes,
                'name': name,
                'parameters': parameters,
                'visualization': visualization,
                'dataset': dataset
            })
        self.write(_id)

    def get(self, action):
        actions = {
            'implementations': self.getProblemClasses
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
