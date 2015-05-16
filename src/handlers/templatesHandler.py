# -*- coding: utf8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, HTTPError, authenticated

import logging


class TemplatesHandler(RequestHandler):
    """Handle requests for html templates"""
    def get(self, filename=None):
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
