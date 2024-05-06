from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"
    
    part_number = fields.Char("Part Number")
    cto = fields.Char("CTO")


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    detail_attribute = fields.Char(string="Detail")