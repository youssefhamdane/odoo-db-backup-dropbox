# -*- coding: utf-8 -*-
{
    'name': "Dropbox Backup",

    'author': "Youssef Hamdane",
    'version': '1',
    'depends': ['base'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/backup_view.xml',
        'data/backup_data.xml',
    ],
    'external_dependencies': {
        'python': ['xmlrpc','dropbox','six'],
     },
    'installable': True,
    'auto_install': False,
}
