from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"
    
    part_number = fields.Char("Part Number")
    cto = fields.Char("CTO")
    