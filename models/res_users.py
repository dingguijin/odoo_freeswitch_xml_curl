# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):

    _inherit = "res.users"

    sip_number = fields.Char('Sip Number', required=False)
    sip_password = fields.Char('Sip Password', required=False)
    

    # update by callcenter and PRESENSE IN
    sip_phone_status = fields.Char('Sip Phone Status', required=False, readonly=True)
    sip_agent_status = fields.Char('Sip Agent Status', required=False, readonly=True)

    # update by presence in
    sip_phone_last_seen = fields.Datetime('Sip Phone Last Seen', required=False, readonly=True)

    # update by register
    sip_register_status = fields.Char('Sip Register Status', required=False, readonly=True)
    sip_phone_user_agent = fields.Char('Sip Phone User Agent', required=False, readonly=True)
    sip_phone_ip = fields.Char('Sip Phone IP', required=False, readonly=True)
    sip_auth_realm = fields.Char('Sip Auth Realm', required=False, readonly=True)

    # update by poll
    user_agent_ip = fields.Char('User Agent IP', required=False, readonly=True)
    user_agent_last_seen = fields.Datetime('User Agent Last Seen', required=False, readonly=True)
