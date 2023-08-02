{
    'name': 'OT Management',
    'version': '1.0',
    'summary': 'Manage OT registration for a company',
    'description': 'This module adds functionality to manage OT registration for a company.',
    'author': 'TranTu',
    'category': '....',
    'depends': ['base', 'mail', 'project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/ot_management_views.xml',
        'views/ot_registration_lines_views.xml',
        'data/employee_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
