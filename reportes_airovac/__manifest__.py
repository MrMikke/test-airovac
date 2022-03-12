# -*- coding: utf-8 -*-
{
    'name': "Presupuesto Airovac",

    'summary': """
        Personalización de presupuesto de ventas""",

    'description': """
        Personalización del presupuesto de ventas
    """,

    'author': "Efecto Negocio",
    'website': "Efectonegocio.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reportes',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/reporte.xml',
        'reports/reporte_ventas_presupuesto_pedido.xml',
        #'reports/efecto_compra_direccion_envio',
        #'reports/oficial.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'auto_install': True,
}
