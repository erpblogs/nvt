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
        if self._context.get('default_super_admin'):
            return self.env.ref(f'custom_users.super_admin').ids
        if self._context.get('default_account_manager'):
            return self.env.ref(f'custom_users.account_manager').ids
        customer_group = self._context.get('default_customer_group')
        if customer_group:
            return self.env.ref(f'custom_users.{customer_group}').ids
            
        default_user_template = 'base.default_user'
        if self._context.get('default_portal_user'):
            default_user_template = 'base.template_portal_user_id'
        default_user_id = self.env['ir.model.data']._xmlid_to_res_id(default_user_template, raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().groups_id if default_user_id else []
    
    portal_user = fields.Boolean("Is Web User")
    super_admin = fields.Boolean("Super Admin")
    account_manager = fields.Boolean("Account Manager")
    groups_id = fields.Many2many(default=_default_groups_custom)
    portal_department_id = fields.Many2one('res.department', 'Department')
    customer_following_ids = fields.One2many('res.partner', 'user_id', string="Customers")
    portal_company_id = fields.Many2one('res.partner', string="Company")
    
    customer_group = fields.Selection([
        ('group_user_sa_manager', 'SA manager'),
        ('group_user_cfo', 'CFO'),
        ('group_user_cooperate', 'Cooperate'),
        ('group_user_employee', 'Employee')
        ], string='Customer Access')

    # @api.model
    # def create(self, vals):
        
    #     if self._context.get('default_portal_user'):
    #         vals.update({
    #             'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
    #         })
    #     return super().create(vals)
    
    @api.onchange('super_admin')
    def onchange_super_admin(self):
        # if self.portal_user:
        if self.super_admin:
            self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.super_admin').id)]
        else:
            self.groups_id = [(3, self.env.ref(f'custom_users.super_admin').id)]
        
    
    @api.onchange('account_manager')
    def onchange_account_manager(self):
        # if self.portal_user:
        if self.account_manager:
            self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.account_manager').id)]
        else:
            self.groups_id = [(3, self.env.ref(f'custom_users.account_manager').id)]
        
    @api.onchange('customer_group')
    def onchange_admin_group(self):
        # if self.portal_user:
        customer_group = self.customer_group or self._context.get('default_customer_group') or 'group_user_employee'
        self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.{customer_group}').id)]
        # else:
        #     admin_group = self.admin_group or self._context.get('default_admin_group') or 'account_manager'
        #     self.groups_id = [(5, 0, 0),] + [(4, self.env.ref(f'custom_users.{admin_group}').id)]

        

    # @api.onchange('customer_following_ids')
    # def onchange_customer_following_ids(self):
    #     if self.customer_following_ids:
    #         self.company_ids = [(6,0, self.company_id.ids + self.customer_following_ids.ids)]
    #     else:
    #         self.company_ids = [(6,0, self.company_id.ids)]
            