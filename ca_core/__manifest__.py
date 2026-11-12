{
    'name': 'Comptabilité Algérienne — Core',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Socle technique commun de Comptabilité Algérienne',
    'license': 'LGPL-3',
    'depends': ['base'],
    'application': False,
    'installable': True,
    'auto_install': False,
    'data': [
        'security/ca_core_groups.xml',
        'security/ir.access.csv',
        'views/accounting_folder_views.xml',
    ],
}
