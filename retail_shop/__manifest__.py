{
    'name': 'Retail Shop',
    'summary': 'Retail Shop Management',
    'description': 'This module helps in managing retail shop operations.',
    'author': 'Ketan Joshi',
    'version': '3.5',
    'sequence': 1,
    'category': 'Sales',

    'data': [
    'security/ir.model.access.csv',
    'data/sale_sequence.xml',
    'views/menus.xml',
    'views/product_views.xml',
    'views/stock_views.xml',
    'views/sale_views.xml',
    'views/profit_views.xml',
    'views/tags_view.xml',
    ],

    'depends': ['base'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',

}