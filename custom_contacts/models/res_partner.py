# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomPartnerInherit(models.Model):
    _inherit = 'res.partner'



# class CustomUserInherit(models.Model):
#     _inherit = 'res.users'

#     customer_following_ids = fields.One2many('res.partner', 'user_id', string="Customers", 
#                                              domain=[('company', '=', True)])