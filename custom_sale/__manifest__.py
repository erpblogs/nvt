# -*- coding: utf-8 -*-
{
    'name': "Custom Sale",

    'summary': "Custom Sale",

    'description': """
Custom Ecommerge
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [ 'sale', 'website_sale', 'delivery', 'sales_team', 'custom_users', 'sale_management', 'product'],

    # always loaded 
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/product_menus.xml',
        'views/sale_menus.xml',
        
        'views/templates.xml',
        'data/mail_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

