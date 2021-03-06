# -*- coding: utf8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, HTTPError
from tornado import gen

import logging
import json

from tools import model
from conf import Conf


class TemplatesHandler(RequestHandler):
    """Handle requests for html templates"""
    def filteredConf(self):
        return {
            'scriptFolders': Conf['scriptFolders'],
            'state': Conf['state']
        }

    @gen.coroutine
    def get(self, template=None):
        if template == 'config.json':
            return self.write(json.dumps(self.filteredConf()))
        # s = yield model.getService('solverTemplates').insert(
        #     type='optimizer', basename='opt', parameters={},
        #     implementation='implem', visualization='viz')
        # print repr(s)
        # p = yield model.getService('problems').insert(
        #     types=[], name='test', parameters={}, implementation='implem',
        #     visualization='testviz', dataset='none')
        # print repr(p)
        # res = yield model.getService('solverInstances').insert(
        #     templateId=s, fullName='optimizer', parameters={},
        #     problemId=p)
        # print repr(res)
        # document = yield model.getService('solverInstances').getById(res)
        # print document
        templateRoutes = {
            'run': 'run.html',
            'compare': 'compare.html',
            'crud-problems': 'problems.html',
            'crud-solvers': 'solvers.html',
            'crud-solutions': 'solutions.html'
        }
        if template is None or not template:
            self.render("run.html", active='run')
        elif not template in templateRoutes:
            logging.error("Unable to find item %s" % template)
            raise HTTPError(404)
        else:
            self.render(templateRoutes[template], active=template)
