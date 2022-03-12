# -*- coding: utf-8 -*-
{
    'name': "Tipo de cambio al registrar pago",

    'summary': """
        Tipo de cambio al registrar pago """,

    'description': """
        Tipo de cambio al registrar pago
        desarrollado por Efecto Negocio
        Dev: Luis Enrique Rodriguez 
    """,

    'author': "Efecto Negocio",
    'website': "https://efectonegocio.com/odoo/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account_accountant',
                'l10n_mx_edi'
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'views/registrar_pagos_facturacion.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
