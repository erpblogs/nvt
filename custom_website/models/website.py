# -*- coding: utf-8 -*-

import re


from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"
    
    website_url = fields.Char(string="Website Url", store=True, compute='_compute_website_url')
    

    @staticmethod
    def convert_to_website_url(text):
        # Replace special characters with underscore
        text = re.sub(r'[^\w\s]', '_', text)
        # Replace multiple spaces with single underscore
        text = re.sub(r'\s+', '_', text)
        # Convert text to lowercase
        text = text.lower()
        # Replace spaces with underscore
        text = text.replace(' ', '_')
        return text
        
    
    @api.depends('name')
    def _compute_website_url(self):
        for r in self:
            if r.id and not r.website_url:
                r.website_url = r.convert_to_website_url(r.name)
        
