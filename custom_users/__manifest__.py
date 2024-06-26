# -*- coding: utf-8 -*-
{
    'name': "Users Management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','auth_signup', 'contacts'],

    # always loaded
    'data': [
        'security/base_group.xml',
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'data/ir_module_category_data.xml',
        
        'views/res_users_view.xml',
        'views/customer_users.xml',
        'views/department_views.xml',
        
        'views/res_partner_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

