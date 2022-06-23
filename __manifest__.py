# -*- coding: utf-8 -*-

{
    'name': 'FreeSWITCH XML CURL',
    'category': 'PPMessage',
    'description': """
    FreeSWITCH XML CURL.
    =========================
    
    """,
    'currency': 'USD',
    'price': '1024',
    'version': '1.0',
    'depends': ['web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/freeswitch_xml_curl.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
    'installable': True,
    'application': True,

    #'auto_install': True,
}
