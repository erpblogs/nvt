# -*- coding: utf-8 -*-

import re


from odoo import models, fields, api, _lt
from odoo.addons.http_routing.models.ir_http import slug


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    
    ec_detail = fields.Html(string="ec Detail", compute="_compute_ec_detail")
    
    @api.depends('')
    def _compute_ec_detail(self):
        for r in self:
            r.ec_detail = r.