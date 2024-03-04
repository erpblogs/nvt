# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

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
            string="Status",
            readonly=False,
            inverse="_inverse_approval_state",
            default='draft')
    
    
    def _inverse_approval_state(self):
        for r in self:
            if r.approval_state in ["confirm", "in_transit", "deliver", ]:
                r.state = 'sale'
            elif r.approval_state == 'cancel':
                r.state = 'draft'
            elif r.approval_state == 'draft':
                r.state = 'sent'
            else:
                r.state = 'cancel'