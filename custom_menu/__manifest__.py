# -*- coding: utf-8 -*-
{
    'name': "Custom Menu",

    'summary': "Custom Menu",

    'description': """
Custom Menu
    """,

    'author': "QuangTV",
    'website': "https://www.erpblogs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'contacts', 'sale', 'spreadsheet_dashboard'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

