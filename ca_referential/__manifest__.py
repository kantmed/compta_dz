{
    'name': 'Comptabilité Algérienne — Referential',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Référentiels communs de Comptabilité Algérienne',
    'license': 'LGPL-3',
    'depends': ['base', 'ca_core', 'ca_audit_log'],
    'data': [
        'security/ir.access.csv',
        'data/legal_forms.xml',
        'data/activity_categories.xml',
        'views/legal_form_views.xml',
        'views/activity_category_views.xml',
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
