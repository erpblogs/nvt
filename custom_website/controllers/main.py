# -*- coding: utf-8 -*-
import json
import logging

from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request, route
from odoo.addons.base.models.ir_qweb_fields import nl2br_enclose
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.sale.controllers import portal as sale_portal
from odoo.osv import expression
from odoo.tools import lazy, str2bool
from odoo.tools.json import scriptsafe as json_scriptsafe

from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute

_logger = logging.getLogger(__name__)

Post_Count = 6
Carousel_Count = 3


class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/shop/categ/<string:category_url>'], type='http', auth="public", website=True)
    def shop_category(self, category_url='', **post):
        Category = request.env['product.public.category']
        if category_url:
            category = Category.search([('website_url', '=', category_url)], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        return request.redirect('/shop/category/%s' % slug(category))
        

    # # @http.route('/category', type='http', auth="user")
    # def index(self, s_action=None, db=None, **kw):
    #     order = 'is_published desc, sequence desc, create_date desc'
    #     Event = request.env['event.event']
    #     News = request.env['blog.post']
    #     # count by domains without self search
    #     domain_search = [('state', '=', 'publish'), ('dp_homepage', '=', True)]
    #     news_domain = domain_search + [('archived_date', '>=', date.today())]
    #     events_domain = domain_search + [('date_end', '>=', datetime.now())]

    #     event_ids = Event.search(events_domain, limit=Post_Count, order=order)
    #     news_ids = News.search(news_domain, limit=Post_Count, order=order)
    #     records = []
    #     if event_ids:
    #         records += [{
    #             'object_model': 'event',
    #             'record_id': event_id
    #         } for event_id in event_ids[0:Carousel_Count]]
    #     if news_ids:
    #         records += [{
    #             'object_model': 'news',
    #             'record_id': news_id
    #         } for news_id in news_ids[0:Carousel_Count]]
    #     values = {
    #         'event_ids': event_ids,
    #         # 'event_carousel_ids': event_ids,
    #         'news_ids': news_ids,
    #         # 'news_carousel_ids': news_ids,
    #         'carousel_ids': records
    #     }
    #     return request.render("website.homepage", values)
