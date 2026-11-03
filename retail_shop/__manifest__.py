{
    'name': 'Retail Shop',
    'version': '1.0',
    'summary': 'Retail Shop Management',
    'description': 'This module helps in managing retail shop operations.',
    'author': 'Ketan Joshi',
    'sequence': 1,
    'category': 'Sales',

    'data': [
    'security/ir.model.access.csv',
    'views/menus.xml',
    'views/product_views.xml',
    'views/stock_views.xml',
    'views/sale_views.xml',
    'views/profit_views.xml',
    ],

    'depends': ['base'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',

}