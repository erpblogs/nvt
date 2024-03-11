# -*- coding: utf-8 -*-
import werkzeug

from werkzeug.exceptions import NotFound, Forbidden
from datetime import date, datetime, timedelta

from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request

Post_Count = 6
Carousel_Count = 3


class Home(Website):

    @http.route('/', type='http', auth="user")
    def index(self, s_action=None, db=None, **kw):
        order = 'is_published desc, sequence desc, create_date desc'
        Event = request.env['event.event']
        News = request.env['blog.post']
        # count by domains without self search
        domain_search = [('state', '=', 'publish'), ('dp_homepage', '=', True)]
        news_domain = domain_search + [('archived_date', '>=', date.today())]
        events_domain = domain_search + [('date_end', '>=', datetime.now())]

        event_ids = Event.search(events_domain, limit=Post_Count, order=order)
        news_ids = News.search(news_domain, limit=Post_Count, order=order)
        records = []
        if event_ids:
            records += [{
                'object_model': 'event',
                'record_id': event_id
            } for event_id in event_ids[0:Carousel_Count]]
        if news_ids:
            records += [{
                'object_model': 'news',
                'record_id': news_id
            } for news_id in news_ids[0:Carousel_Count]]
        values = {
            'event_ids': event_ids,
            # 'event_carousel_ids': event_ids,
            'news_ids': news_ids,
            # 'news_carousel_ids': news_ids,
            'carousel_ids': records
        }
        return request.render("website.homepage", values)
