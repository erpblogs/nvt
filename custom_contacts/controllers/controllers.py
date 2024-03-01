# -*- coding: utf-8 -*-
# from odoo import http


# class NvtUsers(http.Controller):
#     @http.route('/custom_users/custom_users', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_users/custom_users/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_users.listing', {
#             'root': '/custom_users/custom_users',
#             'objects': http.request.env['custom_users.custom_users'].search([]),
#         })

#     @http.route('/custom_users/custom_users/objects/<model("custom_users.custom_users"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_users.object', {
#             'object': obj
#         })

