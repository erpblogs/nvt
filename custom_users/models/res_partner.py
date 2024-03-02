# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.tools import email_normalize
from odoo.exceptions import UserError


DF_TIMEZONE = "Asia/Ho_Chi_Minh"


class CustomPartnerInherit(models.Model):
    _inherit = 'res.partner'
    
    partner_company = fields.Boolean("Is Partner Company")
    tz = fields.Selection(default=DF_TIMEZONE)
    
    signup_token = fields.Char(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")
    signup_type = fields.Char(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")
    signup_expiration = fields.Datetime(groups="base.group_erp_manager,custom_users.super_admin,custom_users.account_manager")

    
    @api.constrains('email')
    def check_valid_email(self):
        for r in self:
            if r.email and not email_normalize(r.email):
                raise UserError(_('Invalid email address %r', r.email))

class ParnerDepartment(models.Model):
    _name = 'res.partner.department'
    _description = "Partner Department"
    
    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.partner', required=True, domain=[('is_company', '=', True), ('partner_company', '=', True)])
    
    

class CustomPartnerCompany(models.Model):
    _inherits = {'res.partner': 'partner_company_id'}
    _name = 'res.partner.company'
    
    partner_company_id = fields.Many2one(comodel_name='res.partner',ondelete='restrict', auto_join=True, index=True)
    # tz = fields.Selection(default=DF_TIMEZONE)
    
    @api.constrains('email')
    def check_valid_email(self):
        for r in self:
            if r.email and not email_normalize(r.email):
                raise UserError(_('Invalid email address %r', r.email))
            
            
# class CustomUsersInherit(models.Model):
#     _inherit = 'res.users'
 
    

# class CustomUserInherit(models.Model):
#     _inherit = 'res.users'

#     customer_following_ids = fields.One2many('res.partner', 'user_id', string="Customers", 
#                                              domain=[('company', '=', True)])