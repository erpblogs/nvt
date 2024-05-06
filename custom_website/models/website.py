# -*- coding: utf-8 -*-

import re


from odoo import models, fields, api, _lt
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
        

class Website(models.Model):
    _inherit = 'website'

         
    def _get_checkout_step_list(self):
        """ Return an ordered list of steps according to the current template rendered.

        :rtype: list
        :return: A list with the following structure:
            [
                [xmlid],
                {
                    'name': str,
                    'current_href': str,
                    'main_button': str,
                    'main_button_href': str,
                    'back_button': str,
                    'back_button_href': str
                }
            ]
        """
        self.ensure_one()
        is_extra_step_active = self.viewref('website_sale.extra_info').active
        redirect_to_sign_in = self.account_on_checkout == 'mandatory' and self.is_public_user()

        steps = [(['website_sale.cart'], {
            'name': _lt("Review Order"),
            'current_href': '/shop/cart',
            'main_button': _lt("Sign In") if redirect_to_sign_in else _lt("Checkout"),
            'main_button_href': f'{"/web/login?redirect=" if redirect_to_sign_in else ""}/shop/checkout',
            # remove ?express=1 to go to the selection address first
            # 'main_button_href': f'{"/web/login?redirect=" if redirect_to_sign_in else ""}/shop/checkout?express=1',
            'back_button':  _lt("Continue shopping"),
            'back_button_href': '/shop',
        }), (['website_sale.checkout', 'website_sale.address'], {
            'name': _lt("Shipping"),
            'current_href': '/shop/checkout',
            'main_button': _lt("Confirm"),
            'main_button_href': f'{"/shop/extra_info" if is_extra_step_active else "/shop/confirm_order"}',
            'back_button':  _lt("Back to cart"),
            'back_button_href': '/shop/cart',
        })]
        
        if is_extra_step_active:
           steps.append((['website_sale.extra_info'], {
                'name': _lt("Extra Info"),
                'current_href': '/shop/extra_info',
                'main_button': _lt("Continue checkout"),
                'main_button_href': '/shop/confirm_order',
                'back_button':  _lt("Return to shipping"),
                'back_button_href': '/shop/checkout',
            }))
           
        steps.append((['website_sale.payment'], {
            'name': _lt("Payment"),
            'current_href': '/shop/payment',
            'back_button':  _lt("Back to cart"),
            'back_button_href': '/shop/cart',
        }))

        return steps