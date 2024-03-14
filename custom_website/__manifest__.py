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
        'data/website_data.xml',
        
        # 'views/savvycom_website_view.xml',
        # website
        
        'views/website_layout.xml',
        'views/website_header.xml',
        'views/web_layout.xml',
        
        # menu
        'views/hidden_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_website/static/src/scss/style.scss'
        ],
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss', 'custom_website/static/src/**/*.variables.scss'),
            ('before', 'web/static/src/scss/primary_variables.scss',  'custom_website/static/src/scss/primary_variables.scss',),
        ],
        'web._assets_secondary_variables': [
            ('before', 'web/static/src/scss/secondary_variables.scss', 'custom_website/static/src/scss/secondary_variables.scss'),
        ],
        'web._assets_common_styles': [
            'custom_website/static/src/scss/fonts.scss',
            # 'vti_theme/static/src/scss/reboot.scss',
            # 'vti_theme/static/src/scss/navbar.scss',
        ],
    }
}

