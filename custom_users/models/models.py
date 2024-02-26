# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomDepartment(models.Model):
    _name = 'res.department'
    _description = "Res Department"
    
    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)


class CustomUserInherit(models.Model):
    _inherit = 'res.users'

    
    def _default_groups_custom(self):
        default_user_template = 'base.default_user'
        if self._context.get('portal_user_template'):
            default_user_template = 'base.template_portal_user_id'
        default_user_id = self.env['ir.model.data']._xmlid_to_res_id(default_user_template, raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().groups_id if default_user_id else []
    
    web_user = fields.Boolean("Is Web User")
    is_manager = fields.Boolean("Is Manager")
    groups_id = fields.Many2many(default=_default_groups_custom)
    portal_department_id = fields.Many2one('res.department', 'Department')
    portal_company_following_ids = fields.Many2many('res.company', 'portal_user_company_ref',
                                                    string="Company Following", domain="[('web_company', '=', True)]")
    

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
            self.groups_id = [(4, self.env.ref('custom_users.group_portal_admin').id)]
        else:
            self.groups_id = [(3, self.env.ref('custom_users.group_portal_admin').id)]