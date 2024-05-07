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
from odoo.addons.portal.controllers.portal import CustomerPortal


from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

Post_Count = 6
Carousel_Count = 3


TRUSTED_DEVICE_COOKIE = 'td_id'
TRUSTED_USER_COOKIE = 'pre_uid'
REMEMBER_COOKIE = 'remember'
TRUSTED_DEVICE_AGE = 90 * 86400


INCORRECT_EMAIL_WARNING = _('Your email was incorrect. Please try again.')
INACTIVE_EMAIL_WARNING = _('This email address is no longer active. Please use a different account to log in.')
WRONG_EMAIL_PASSWORD = _("Wrong email or password. Please try again.")
WRONG_EMAIL_FORMAT = _('Wrong email format. Please try again.')


class AuthSignupHome(Home):
    
    @http.route()
    def web_login(self, redirect=None, **kw):

        response = super().web_login(redirect, **kw)

        not_admin = response.qcontext.get('login', '') != 'admin'
        if not_admin and response.qcontext.get('login') and not tools.email_normalize(
                response.qcontext.get('login', '')):
            response.qcontext['account_error'] = WRONG_EMAIL_FORMAT

        elif response.qcontext.get('error') and not request.params.get('oauth_error'):
            response.qcontext['error'] = WRONG_EMAIL_PASSWORD
            if response.qcontext.get('login'):
                user_count = request.env['res.users'].sudo().search([
                    ('login', '=ilike', response.qcontext['login']),
                    ('active', 'in', [True, False])
                ])
                if not user_count:
                    response.qcontext['account_error'] = INCORRECT_EMAIL_WARNING
                elif not user_count.active:
                    response.qcontext['account_error'] = INACTIVE_EMAIL_WARNING

        if kw.get('remember'):
            name = _("%(browser)s on %(platform)s",
                     browser=request.httprequest.user_agent.browser.capitalize(),
                     platform=request.httprequest.user_agent.platform.capitalize(),
                     )

            if request.geoip.city.name:
                name += f" ({request.geoip.city.name}, {request.geoip.country_name})"

            key = request.env['auth_totp.device']._generate("browser", name)
            response.set_cookie(
                key=TRUSTED_DEVICE_COOKIE,
                value=key,
                max_age=TRUSTED_DEVICE_AGE,
                httponly=True,
                samesite='Lax',

            )

            # start thêm remember vào coockies
            response.set_cookie(
                key=REMEMBER_COOKIE,
                value=kw.get('remember'),
                max_age=TRUSTED_DEVICE_AGE,
                httponly=True,
                samesite='Lax',

            )
            # end thêm remember vào coockies

            if request.session.uid:
                response.set_cookie(
                    key=TRUSTED_USER_COOKIE,
                    value=f'{request.session.uid}',
                    max_age=TRUSTED_DEVICE_AGE,
                    httponly=True,
                    samesite='Lax',
                )

            # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@)
            request.session.touch()
        else:
            response.delete_cookie(REMEMBER_COOKIE)

        if not request.session.uid:

            cookies = request.httprequest.cookies
            pre_uid = cookies.get(TRUSTED_USER_COOKIE)
            user = None
            try:
                user = request.env['res.users'].sudo().browse(int(pre_uid))
            except:
                pass
            key = cookies.get(TRUSTED_DEVICE_COOKIE)
            remember = cookies.get(REMEMBER_COOKIE)
            if key and user:
                user_match = request.env['auth_totp.device']._check_credentials_for_uid(
                    scope="browser", key=key, uid=user.id)
                if user_match:
                    if remember:
                        # request.session.finalize(request.env)
                        # kw['login'] = user.login
                        response.qcontext['login'] = user.login
                        response.qcontext['remember'] = True

        return response


class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/shop/categ/<string:category_url>'], type='http', auth="public", website=True)
    def shop_category(self, category_url='', **post):
        Category = request.env['product.public.category']
        if category_url:
            category = Category.search([('website_url', '=', category_url)], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        return request.redirect('/shop/category/%s' % slug(category))
        

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()
        website_domain = website.website_domain()
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = website.shop_ppg or 20

        ppr = website.shop_ppr or 4

        request_args = request.httprequest.args
        attrib_list = request_args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        filter_by_tags_enabled = website.is_view_active('website_sale.filter_products_tags')
        # alway active 
        # filter_by_tags_enabled = True
        
        if filter_by_tags_enabled:
            tags = request_args.getlist('tags')
            # Allow only numeric tag values to avoid internal error.
            if tags and all(tag.isnumeric() for tag in tags):
                post['tags'] = tags
                tags = {int(tag) for tag in tags}
            else:
                post['tags'] = None
                tags = {}

        keep = QueryURL('/shop', **self._shop_get_query_url_kwargs(category and int(category), search, min_price, max_price, **post))

        now = datetime.timestamp(datetime.now())
        pricelist = website.pricelist_id
        if 'website_sale_pricelist_time' in request.session:
            # Check if we need to refresh the cached pricelist
            pricelist_save_time = request.session['website_sale_pricelist_time']
            if pricelist_save_time < now - 60*60:
                request.session.pop('website_sale_current_pl', None)
                website.invalidate_recordset(['pricelist_id'])
                pricelist = website.pricelist_id
                request.session['website_sale_pricelist_time'] = now
                request.session['website_sale_current_pl'] = pricelist.id
        else:
            request.session['website_sale_pricelist_time'] = now
            request.session['website_sale_current_pl'] = pricelist.id

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.sudo().currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, website.currency_id, request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        url = '/shop'
        if search:
            post['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            display_currency=website.currency_id,
            **post
        )
        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search, website)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            # TODO Find an alternative way to obtain the domain through the search metadata.
            Product = request.env['product.template'].with_context(bin_size=True)
            domain = self._get_shop_domain(search, category, attrib_values)

            # This is ~4 times more efficient than a search for the cheapest and most expensive products
            query = Product._where_calc(domain)
            Product._apply_ir_rules(query, 'read')
            from_clause, where_clause, where_params = query.get_sql()
            query = f"""
                SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                  FROM {from_clause}
                 WHERE {where_clause}
            """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()

            if min_price or max_price:
                # The if/else condition in the min_price / max_price value assignment
                # tackles the case where we switch to a list of products with different
                # available min / max prices than the ones set in the previous page.
                # In order to have logical results and not yield empty product lists, the
                # price filter is set to their respective available prices when the specified
                # min exceeds the max, and / or the specified max is lower than the available min.
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price

        ProductTag = request.env['product.tag']
        if filter_by_tags_enabled and search_product:
            all_tags = ProductTag.search(
                expression.AND([
                    [('product_ids.is_published', '=', True), ('visible_on_ecommerce', '=', True)],
                    website_domain
                ])
            )
        else:
            all_tags = ProductTag

        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = lazy(lambda: Category.search(categs_domain))

        if category:
            url = "/shop/category/%s" % slug(category)

        pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=5, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = lazy(lambda: ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ]))
        else:
            attributes = lazy(lambda: ProductAttribute.browse(attributes_ids))

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
            request.session['website_sale_shop_layout_mode'] = layout_mode

        # Try to fetch geoip based fpos or fallback on partner one
        fiscal_position_sudo = website.fiscal_position_id.sudo()
        products_prices = lazy(lambda: products._get_sales_prices(pricelist, fiscal_position_sudo))

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'order': post.get('order', ''),
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'fiscal_position': fiscal_position_sudo,
            'add_qty': add_qty,
            'products': products,
            'search_product': search_product,
            'search_count': product_count,  # common for all searchbox
            'bins': lazy(lambda: TableCompute().process(products, ppg, ppr)),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'products_prices': products_prices,
            'get_product_prices': lambda product: lazy(lambda: products_prices[product.id]),
            'float_round': tools.float_round,
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(available_min_price, 2)
            values['available_max_price'] = tools.float_round(available_max_price, 2)
        if filter_by_tags_enabled:
            values.update({'all_tags': all_tags, 'tags': tags})

        if category:
            values['main_object'] = category
        values.update(self._get_additional_shop_values(values))
        
        # return request.render("website_sale.products", values)
        return request.render("custom_website.products", values)
    
    
    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        return request.render("website_sale.product", self._prepare_product_values(product, category, search, **kwargs))
        
 
    def _prepare_product_values(self, product, category, search, **kwargs):
        ProductCategory = request.env['product.public.category']
        if not category and product.public_categ_ids:
            category = product.public_categ_ids[0]
        # category = ProductCategory.browse(int(category)).exists()
        try:
            category = ProductCategory.browse(int(category)).exists()
        except:
            raise ValidationError(_("Product public category does not exits!"))
                
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL(
            '/shop',
            **self._product_get_query_url_kwargs(
                category=category,
                search=search,
                **kwargs,
            ),
        )

        # Needed to trigger the recently viewed product rpc
        view_track = request.website.viewref("website_sale.product").track

        return {
            'search': search,
            'category': category,
            'pricelist': request.website.pricelist_id,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': ProductCategory.search([('parent_id', '=', False)]),
            'main_object': product,
            'product': product,
            'add_qty': 1,
            'view_track': view_track,
        }
    
    
    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if request.website.is_public_user():
            return request.redirect('/web/login?redirect=/shop/cart')
            
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                # Retrieve the last known order from the session if the session key `sale_order_id`
                # was prematurely cleared. This is done to prevent the user from updating their cart
                # after payment in case they don't return from payment through this route.
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')


        # tobe add code to check history request
        errors = self._get_shop_payment_errors(order)
        if errors:
            first_error = errors[0]  # only display first error
            error_msg = f"{first_error[0]}\n{first_error[1]}"
            raise ValidationError(error_msg)

        if not order:
            return request.redirect('/shop')
        
        order.with_context(send_email=True).with_user(SUPERUSER_ID).action_send_request()
        return request.redirect(order.get_portal_url())
   
   
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order_sudo = request.website.sale_get_order()

        redirection = self.checkout_redirection(order_sudo)
        if redirection:
            return redirection

        # if order_sudo._is_public_order():
        #     return request.redirect('/shop/address')

        redirection = self.checkout_check_address(order_sudo)
        if redirection:
            return redirection

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values = self.checkout_values(order_sudo, **post)

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

class OnlineSynchronizationPortal(CustomerPortal):
   
    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, **kwargs):
        values = self._prepare_sale_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_orders_history'] = values['orders'].ids[:100]
        
        return request.render("sale.portal_my_orders", values)
        return request.render("custom_website.custom_portal_my_orders", values)

    def _prepare_orders_custom_domain(self, partner, state=False):
        default_domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id])
        ]
        if state:
            default_domain.append(('approval_state', '=', state))
        return default_domain
    
    def _prepare_sale_request_information(self):
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        # Total Request
        total_rq = SaleOrder.search_count(self._prepare_orders_custom_domain(partner))
        done_rq = SaleOrder.search_count(self._prepare_orders_custom_domain(partner, 'done'))
        draft_rq = SaleOrder.search_count(self._prepare_orders_custom_domain(partner, 'draft'))
        
        return total_rq, done_rq, draft_rq
        
        
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            if not partner.can_edit_vat():
                post['country_id'] = str(partner.country_id.id)

            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self._get_mandatory_fields()}
                values.update({key: post[key] for key in self._get_optional_fields() if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        total_rq, done_rq, draft_rq = self._prepare_sale_request_information()
    
        # partner address 
        # ('group_user_sa_manager', 'SA manager'),
        # ('group_user_cfo', 'CFO'),
        # ('group_user_cooperate', 'Cooperate'),
        # ('group_user_employee', 'Employee')
        # ], string='Role')
        if request.env.user.customer_group in ['group_user_sa_manager', 'group_user_cfo']:
            address_ids = request.env.user.portal_company_id and request.env.user.portal_company_id.address_ids
        else:
            address_ids = partner.address_ids
        
        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'address_ids': address_ids,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
            'total_rq': total_rq,
            'done_rq': done_rq,
            'draft_rq': draft_rq,
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


