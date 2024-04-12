# -*- coding: utf-8 -*-
{
    'name': 'EMSG MRP MPS for MacD',
    'summary': "EMSG MRP MPS for MacD",
    'description': 'EMSG MRP MPS for MacD',

    'category': 'Production',
    'version': '17.0.0.1.0',
    'depends': ['mrp', 'mrp_mps'],

    'data': [
        'security/ir.model.access.csv',
        'data/mrp_data.xml',
        'views/mrp_mps_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'emsg_mrp_mps/static/src/**/*',
        ],
    },

    'installable': True,
    'application': False,
}
