{
    'name': 'Comptabilité Algérienne — Mandates',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gestion des mandats entre cabinets comptables et sociétés clientes',
    'license': 'LGPL-3',
    'depends': ['base', 'ca_core', 'ca_accounting_folder', 'ca_company_profile', 'ca_audit_log'],
    'data': [
        'data/ir_sequence.xml',
        'data/mandate_missions.xml',
        'security/ir.access.csv',
        'views/mandate_views.xml',
        'views/mandate_mission_views.xml',
        'views/menus.xml',
    ],
    'i18n': [
        'i18n/fr.po',
        'i18n/ar.po',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
