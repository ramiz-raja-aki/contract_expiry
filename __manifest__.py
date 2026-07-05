{
    'name': 'Contract Expiry Notification',
    'version': '18.0.1.0.0',
    'summary': 'Send activity notifications before employee contract expiry',
    'description': """
        Sends activity notifications to selected users 15 days before
        employee contract expiry. Users can opt-in via their user settings
        by enabling the 'Contract Expiry Notification' field.
    """,
    'category': 'Human Resources',
    'author': 'AKI',
    'depends': ['hr_contract', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
