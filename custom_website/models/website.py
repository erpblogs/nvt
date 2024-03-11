# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SavvyComWebsite(models.Model):
    _name = 'savvycom.website'
    
    name = fields.Char(string="Website Name", required=True, )
    company_id = fields.Many2one('res.company', required=False, default=False)
    company_name = fields.Char(string="Website Name", required=False, )
    
    
    
    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.company_name = self.company_id.name
    