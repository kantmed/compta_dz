{
    'name': 'Comptabilité Algérienne — Company Profile',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Profil juridique, administratif et fiscal des sociétés',
    'license': 'LGPL-3',
    'depends': ['base', 'ca_core', 'ca_referential', 'ca_audit_log'],
    'data': [
        'views/res_company_views.xml',
    ],
    'i18n': [
        'i18n/fr.po',
        'i18n/ar.po',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
