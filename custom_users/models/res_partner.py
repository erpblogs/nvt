# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class NvtCompanyInherit(models.Model):
#     _inherit = 'res.company'

#     web_company = fields.Boolean("Web Company")

#     @api.model_create_multi
#     def create(self, vals_list):
#         company_ids = super().create(vals_list)
#         self._add_company_to_admin(company_ids)

#         return company_ids  

#     def _add_company_to_admin(self, company_ids):
#         system_admin_ids = self.env.ref('base.group_system')
#         super_admin_ids = self.env.ref('custom_users.super_admin')
#         admin_ids = system_admin_ids.users + super_admin_ids.users
#         admin_ids.company_ids = [(4, company.id) for company in company_ids]