# -*- coding: utf-8 -*-
import werkzeug

from werkzeug.exceptions import NotFound, Forbidden
from datetime import date, datetime, timedelta

from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request


class Home(Website):
    
    @http.route('/', auth="public", website=True, sitemap=True)
    def index(self, **kw):
    # @http.route('/', type='http', auth="user")
        Product = request.env['product.template']
        # count by domains without self search
        domain_search = [('priority', '=', '1')]

        highlight_product_ids = Product.search(domain_search, limit=20)
        categories = [
            'mac-macbook-pro',
            'mac-macbook-air',
            'iphone',
            'ipad',
            'airpods-airpods-pro',
            'watch',
        ]
        
        values = {
            'highlight_product_ids': highlight_product_ids,
            'categories': categories
        }
        return request.render("website.homepage", values)
