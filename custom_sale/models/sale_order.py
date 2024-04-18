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
    old_state = fields.Selection(
            selection=APPROVAL_STATE,
            string="Old Status",
            compute='compute_approval_state',
            readonly=False, store=True,
            default='draft')

    def compute_approval_state(self):
        for r in self:
            if r.approval_state:
                r.old_state = r.approval_state
            else:
                r.old_state = False

    
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
            template = self.env.ref('custom_sale.mail_template_change_stage_sale')

            template.send_mail(r.id)
            r.old_state = r.approval_state

    def get_old_state(self):
         if self.old_state:
             return dict(self._fields['old_state']._description_selection(self.env)).get(self.old_state)

    def get_new_state(self):
         if self.approval_state:
             return dict(self._fields['old_state']._description_selection(self.env)).get(self.approval_state)
    
    
    def action_send_request(self):
        for r in self:
            # r.write({'approval_state': 'draft', 'state': 'sent',})
            r.approval_state = 'draft'
            r.action_confirm()