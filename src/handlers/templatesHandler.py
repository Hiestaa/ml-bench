# -*- coding: utf8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, HTTPError, authenticated
from tornado import gen

import logging

from tools import model


class TemplatesHandler(RequestHandler):
    """Handle requests for html templates"""
    @gen.coroutine
    def get(self, filename=None):
        s = yield model.getService('solverTemplates').insert(
            type='optimizer', basename='opt', parameters={},
            implementation='implem', visualization='viz')
        print repr(s)
        p = yield model.getService('problems').insert(
            types=[], name='test', parameters={}, implementation='implem',
            visualization='testviz', dataset='none')
        print repr(p)
        res = yield model.getService('solverInstances').insert(
            templateId=s, fullName='optimizer', parameters={},
            problemId=p)
        print repr(res)
        document = yield model.getService('solverInstances').getById(res)
        print document
        templateRoutes = {
            'ui': 'ui.html'
        }
        if filename is None or not filename:
            self.render("ui.html")
        elif not filename in templateRoutes:
            logging.error("Unable to find item %s" % filename)
            raise HTTPError(404)
        else:
            self.render(templateRoutes[filename])
