# -*- coding: utf-8 -*-
{
    'name': "Custom Website",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'website',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'website'],

    # always loaded
    'data': [
        # 'security/base_group.xml',
        # 'security/base_security.xml',
        'security/ir.model.access.csv',
        
        # datas
        'data/company.xml',
        'data/website_date.xml',
        
        'views/savvycom_website_view.xml',
        # website
        
        'views/website_templates.xml',
        
        # menu
        'views/hidden_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

