{
    'name': 'OT Management',
    'version': '1.0',
    'summary': 'Manage OT registration for a company',
    'description': 'This module adds functionality to manage OT registration for a company.',
    'author': 'TranTu',
    'category': '....',
    'depends': ['base', 'mail','ot.request'],
    'data': [
        'security/ir.model.access.csv',
        'views/ot_request_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
