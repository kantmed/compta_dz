{
    'name': 'Comptabilité Algérienne — Audit Log',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Traçabilité et journalisation des opérations sensibles',
    'license': 'LGPL-3',
    'depends': ['ca_core', 'ca_accounting_folder'],
    'data': [
        'security/ca_audit_log_groups.xml',
        'security/ir.access.csv',
        'views/audit_log_views.xml',
    ],
    'i18n': [
        'i18n/fr.po',
        'i18n/ar.po',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
