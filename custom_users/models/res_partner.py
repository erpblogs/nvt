# -*- coding: utf-8 -*-

from odoo import models, fields, api


DF_TIMEZONE = "Asia/Ho_Chi_Minh"


class ParnerDepartment(models.Model):
    _name = 'res.partner.department'
    _description = "Partner Department"
    
    name = fields.Char("Name")
    company_id = fields.Many2one('res.partner', required=True, domain=[('is_company', '=', True)])
    
    

class CustomPartnerInherit(models.Model):
    _inherit = 'res.partner'
    
    partner_company = fields.Boolean("Is Partner Company")
    partner_department_id = fields.Many2one('res.partner.department', string="Department")
    tz = fields.Selection(default=DF_TIMEZONE)
    
    signup_token = fields.Char(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")
    signup_type = fields.Char(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")
    signup_expiration = fields.Datetime(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")

# class CustomUsersInherit(models.Model):
#     _inherit = 'res.users'
 
    

# class CustomUserInherit(models.Model):
#     _inherit = 'res.users'

#     customer_following_ids = fields.One2many('res.partner', 'user_id', string="Customers", 
#                                              domain=[('company', '=', True)])