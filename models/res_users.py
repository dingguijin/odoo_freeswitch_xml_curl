# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):

    _inherit = "res.users"

    sip_number = fields.Char('Sip Number', required=False)
    sip_password = fields.Char('Sip Password', required=False)
    
    sip_register_status = fields.Char('Sip Register Status', required=False, readonly=True)
    sip_phone_status = fields.Char('Sip Phone Status', required=False, readonly=True)
    sip_agent_status = fields.Char('Sip Agent Status', required=False, readonly=True)
    
    sip_phone_user_agent = fields.Char('Sip Phone User Agent', required=False, readonly=True)
    sip_phone_last_seen = fields.Datetime('Sip Phone Last Seen', required=False, readonly=True)

    sip_phone_ip = fields.Char('Sip Phone IP', required=False, readonly=True)
    sip_auth_realm = fields.Char('Sip Auth Realm', required=False, readonly=True)
