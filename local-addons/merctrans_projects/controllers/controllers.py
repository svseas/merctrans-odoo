# -*- coding: utf-8 -*-
# from odoo import http


# class MerctransProjects(http.Controller):
#     @http.route('/merctrans_projects/merctrans_projects/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/merctrans_projects/merctrans_projects/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('merctrans_projects.listing', {
#             'root': '/merctrans_projects/merctrans_projects',
#             'objects': http.request.env['merctrans_projects.merctrans_projects'].search([]),
#         })

#     @http.route('/merctrans_projects/merctrans_projects/objects/<model("merctrans_projects.merctrans_projects"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('merctrans_projects.object', {
#             'object': obj
#         })
