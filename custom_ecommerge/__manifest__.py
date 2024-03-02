# -*- coding: utf-8 -*-
{
    'name': "Custom Ecommerge",

    'summary': "Custom Ecommerge",

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
    'depends': [ 'sales_team', 'custom_menu',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        
        'views/product_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

