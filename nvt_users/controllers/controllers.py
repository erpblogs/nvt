# -*- coding: utf-8 -*-
# from odoo import http


# class NvtUsers(http.Controller):
#     @http.route('/nvt_users/nvt_users', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nvt_users/nvt_users/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nvt_users.listing', {
#             'root': '/nvt_users/nvt_users',
#             'objects': http.request.env['nvt_users.nvt_users'].search([]),
#         })

#     @http.route('/nvt_users/nvt_users/objects/<model("nvt_users.nvt_users"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nvt_users.object', {
#             'object': obj
#         })

