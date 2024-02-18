# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NvtCompanyInherit(models.Model):
    _inherit = 'res.company'

    web_company = fields.Boolean("Web Company")
