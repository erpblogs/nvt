# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NvtUserInherit(models.Model):
    _inherit = 'res.users'

    
    def _default_groups_custom(self):
        default_user_template = 'base.default_user'
        if self._context.get('portal_user_template'):
            default_user_template = 'base.template_portal_user_id'
        default_user_id = self.env['ir.model.data']._xmlid_to_res_id(default_user_template, raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().groups_id if default_user_id else []
    
    is_manager = fields.Boolean("Is Manager")
    groups_id = fields.Many2many(default=_default_groups_custom)
    

    # @api.model
    # def create(self, vals):
        
    #     if self._context.get('default_portal_user'):
    #         vals.update({
    #             'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
    #         })
    #     return super().create(vals)
    
    @api.onchange('is_manager')
    def onchange_is_manager(self):
        if self.is_manager:
            self.groups_id = [(4, self.env.ref('custom_users.group_partner_approval').id)]
        else:
            self.groups_id = [(3, self.env.ref('custom_users.group_partner_approval').id)]