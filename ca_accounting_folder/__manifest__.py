{
    'name': 'Comptabilité Algérienne — Accounting Folder',
    'version': '20.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Rattachement des documents comptables natifs à un dossier comptable',
    'license': 'LGPL-3',
    'depends': ['ca_core', 'account'],
    'data': [
        'security/ir.access.csv',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/accounting_folder_views.xml',
    ],
    'i18n': [
        'i18n/fr.po',
        'i18n/ar.po',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
