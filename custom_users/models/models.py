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
    
    user_group = fields.Selection([
        ('group_user_account_manager', 'Account Manager'),
        ('group_user_sa_manager', 'SA manager'),
        ('group_user_cfo', 'CFO')
        ], string='Users Access')

    portal_group = fields.Selection([
        ('group_user_cooperate', 'Cooperate'),
        ('group_user_employee', 'Employee')
        ], string='Portal Access')

    # @api.model
    # def create(self, vals):
        
    #     if self._context.get('default_portal_user'):
    #         vals.update({
    #             'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
    #         })
    #     return super().create(vals)
    
    @api.onchange('portal_group', 'user_group', 'web_user')
    def onchange_user_group(self):
        if self.web_user:
            portal_group = self.portal_group or self._context.get('default_portal_group') or 'group_user_employee'
            self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.{portal_group}').id)]
        else:
            user_group = self.user_group or self._context.get('default_user_group') or 'group_user_account_manager'
            self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.{user_group}').id)]

        

        