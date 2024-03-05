# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

# confirm,pending, in transit , delivered., canceled

APPROVAL_STATE = [
    ('draft', "Pending"),
    ('confirm', "Confirmed"),
    ('in_transit', "In transit"),
    ('deliver', "Delivered"),
    ('cancel', "Cancelled"),
]


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    approval_state = fields.Selection(
            selection=APPROVAL_STATE,
            string="Approval Status",
            readonly=False, store=True, 
            inverse="_inverse_approval_state",
            default='draft')
    
    @api.onchange('approval_state')
    def _inverse_approval_state(self):
        for r in self:
            if r.approval_state == 'cancel':
                r.state = 'cancel'
            elif r.approval_state == 'confirm':
                r.state = 'sent'
            elif r.approval_state == 'draft':
                r.state = 'draft'
            else:
                r.state = 'sale'
                
    