# -*- coding: utf-8 -*-
{
    'name': "darfchain",

    'summary': """
        Module for Distributed Accounting Resource and Finance system in blockChain""",

    'description': """
        The system of accounting, management and analysis of financial obligations in projects and communities on the detachment with semantic smart contracts constructor
    """,

    'author': "DARFChain Stanislav Stanta Taktaev",
    'website': "http://www.darfchain.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Blockchain',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}