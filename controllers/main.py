# -*- coding: utf-8 -*-

from odoo import http

import logging


_EMPTY_XML = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
<section name="result">
<result status="not found" />
</section>
</document>
"""


_CONFIGURATION_XML_TEMPLATE = """
<document type="freeswitch/xml">
<section name="configuration">
  
<configuration name="%s.conf" description="%s">
%s
</configuration>
 
</section>
</document>
"""

_logger = logging.getLogger(__name__)

class FreeSwitchXmlCurl(http.Controller):
    def _get_freeswitch_ip(self):
        _model = http.request.env["freeswitch_xml_curl.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            return None
        return _ss[0].get("freeswitch_ip")
    
    def _get_freeswitch_password(self):
        _model = http.request.env["freeswitch_xml_curl.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            return None
        return _ss[0].get("freeswitch_password")

    def _get_key_value(self):
        if http.request.params.get("key_name") != "name":
            return None
        return http.request.params.get("key_value")

    def _is_key_value(self, value):
        return self._get_key_value() == value
    
    def _is_section_name_matched(self, name):
        if http.request.params.get("section") != name:
            return False
        # directory tag_name is domain
        # if http.request.params.get("tag_name") != name:
        #     return False
        return True

    def _is_purpose_matched(self, purpose):
        if http.request.params.get("purpose") == purpose:
            return True
        return False
    
    def _is_action_matched(self, action):
        if http.request.params.get("action") == action:
            return True
        return False

    def _is_hostname_matched(self):
        _freeswitch_hostname = "freeswitch_hostname"
        _model = http.request.env["freeswitch_xml_curl.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            _logger.error("No freeswitch record")
            return False

        if  len(_ss) > 1:
            _logger.error("Too many freeswitchs record")
            return False

        _hostname = http.request.params.get("hostname")
        _hostname_config = _ss[0].get("freeswitch_hostname")
        if _hostname in [_hostname_config, _hostname_config + ".local"]:
            return True
        
        _logger.error("Freeswitch name not matched, expect %s, but %s" % (_ss[0].get("freeswitch_hostname"), http.request.params.get("hostname")))
        return False

    def _xml_cdr_conf(self):
        _content = """
        <settings>
        <param name="url" value="http://127.0.0.1:8069/freeswitch_xml_cdr"/>
        <param name="retries" value="2"/>
        <param name="delay" value="120"/>
        <param name="log-dir" value="/var/log/cdr"/>
        <param name="err-log-dir" value="/var/log/cdr/errors"/>
        <param name="encode" value="True"/>
        </settings>
        """
        _xml = _CONFIGURATION_XML_TEMPLATE % ("xml_cdr", "xml_cdr", _content)
        return _xml

    def _sofia_conf_config_sofia(self):
        _template = """        
        <global_settings>
        <param name="log-level" value="0"/>
        <param name="debug-presence" value="0"/>
        </global_settings>

        <profiles>

        <profile name="internal">
        <domains>
        <domain name="all" alias="true" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="watchdog-enabled" value="no"/>
        <param name="watchdog-step-timeout" value="30000"/>
        <param name="watchdog-event-timeout" value="30000"/>
        
        <param name="log-auth-failures" value="false"/>
        <param name="forward-unsolicited-mwi-notify" value="false"/>
        
        <param name="context" value="public"/>
        <param name="rfc2833-pt" value="101"/>
        <param name="sip-port" value="$${internal_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>

        <param name="hold-music" value="$${hold_music}"/>
        <param name="apply-nat-acl" value="nat.auto"/>
        <param name="apply-inbound-acl" value="domains"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="record-path" value="$${recordings_dir}"/>
        <param name="record-template" value="${caller_id_number}.${target_domain}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        <param name="manage-presence" value="true"/>
        <param name="presence-hosts" value="$${domain},$${local_ip_v4}"/>
        <param name="presence-privacy" value="$${presence_privacy}"/>
        <param name="inbound-codec-negotiation" value="generous"/>

        <param name="tls" value="$${internal_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${internal_tls_port}"/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-version" value="$${sip_tls_version}"/>
        <param name="tls-ciphers" value="$${sip_tls_ciphers}"/>

        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/>
        <param name="nonce-ttl" value="60"/>
        
        <param name="auth-calls" value="$${internal_auth_calls}"/>
        <param name="inbound-reg-force-matching-username" value="true"/>
        <param name="auth-all-packets" value="false"/>
        
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>
        
        <param name="force-register-domain" value="$${domain}"/>
        <param name="force-subscription-domain" value="$${domain}"/>
        <param name="force-register-db-domain" value="$${domain}"/>

        <param name="ws-binding"  value=":5066"/>
        <param name="wss-binding" value=":7443"/>
        <param name="challenge-realm" value="auto_from"/>
        
        </settings>
        </profile>

        <profile name="external"> 
        <domains>
        <domain name="all" alias="false" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="rfc2833-pt" value="101"/>

        <param name="sip-port" value="$${external_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="context" value="public"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${outbound_codec_prefs}"/>
        <param name="hold-music" value="$${hold_music}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="manage-presence" value="false"/>

        <param name="inbound-codec-negotiation" value="generous"/>
        <param name="nonce-ttl" value="60"/>
        <param name="auth-calls" value="false"/>
        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/> <!-- (also enables late negotiation) -->
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>

        <param name="tls" value="$${external_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${external_tls_port}"/>
        <param name="tls-passphrase" value=""/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-verify-in-subjects" value=""/>
        <param name="tls-version" value="$${sip_tls_version}"/>
        </settings>

        <gateways>
        {{GATEWAYS}}
        </gateways>
        </profile>         
        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)

        return _xml

    def _sofia_conf_internal(self):
        _template = """        

        <profiles>

        <profile name="internal">
        <domains>
        <domain name="all" alias="true" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="watchdog-enabled" value="no"/>
        <param name="watchdog-step-timeout" value="30000"/>
        <param name="watchdog-event-timeout" value="30000"/>
        
        <param name="log-auth-failures" value="false"/>
        <param name="forward-unsolicited-mwi-notify" value="false"/>
        
        <param name="context" value="public"/>
        <param name="rfc2833-pt" value="101"/>
        <param name="sip-port" value="$${internal_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>

        <param name="hold-music" value="$${hold_music}"/>
        <param name="apply-nat-acl" value="nat.auto"/>
        <param name="apply-inbound-acl" value="domains"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="record-path" value="$${recordings_dir}"/>
        <param name="record-template" value="${caller_id_number}.${target_domain}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        <param name="manage-presence" value="true"/>
        <param name="presence-hosts" value="$${domain},$${local_ip_v4}"/>
        <param name="presence-privacy" value="$${presence_privacy}"/>
        <param name="inbound-codec-negotiation" value="generous"/>

        <param name="tls" value="$${internal_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${internal_tls_port}"/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-version" value="$${sip_tls_version}"/>
        <param name="tls-ciphers" value="$${sip_tls_ciphers}"/>

        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/>
        <param name="nonce-ttl" value="60"/>
        
        <param name="auth-calls" value="$${internal_auth_calls}"/>
        <param name="inbound-reg-force-matching-username" value="true"/>
        <param name="auth-all-packets" value="false"/>
        
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>
        
        <param name="force-register-domain" value="$${domain}"/>
        <param name="force-subscription-domain" value="$${domain}"/>
        <param name="force-register-db-domain" value="$${domain}"/>

        <param name="ws-binding"  value=":5066"/>
        <param name="wss-binding" value=":7443"/>
        <param name="challenge-realm" value="auto_from"/>
        
        </settings>
        </profile>
        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)
        
        return _xml

    def _sofia_conf_external(self):
        _template = """        

        <profiles>

        <profile name="external"> 
        <domains>
        <domain name="all" alias="false" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="rfc2833-pt" value="101"/>

        <param name="sip-port" value="$${external_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="context" value="public"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${outbound_codec_prefs}"/>
        <param name="hold-music" value="$${hold_music}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="manage-presence" value="false"/>

        <param name="inbound-codec-negotiation" value="generous"/>
        <param name="nonce-ttl" value="60"/>
        <param name="auth-calls" value="false"/>
        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/> <!-- (also enables late negotiation) -->
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>

        <param name="tls" value="$${external_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${external_tls_port}"/>
        <param name="tls-passphrase" value=""/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-verify-in-subjects" value=""/>
        <param name="tls-version" value="$${sip_tls_version}"/>
        </settings>

        <gateways>
        {{GATEWAYS}}
        </gateways>
        </profile>         

        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)

        return _xml
    
    def _sofia_conf(self):
        if http.request.params.get("Event-Calling-Function") == "config_sofia":
            return self._sofia_conf_config_sofia()

        if http.request.params.get("Event-Calling-Function") == "launch_sofia_worker_thread":
            if http.request.params.get("profile") == "internal":
                return self._sofia_conf_internal()
            if http.request.params.get("profile") == "external":
                return self._sofia_conf_external()
        _logger.error("Unknown sofia conf request:  [%s]" % http.request.params)
        return _EMPTY_XML
    
    def _conference_conf(self):
        return _EMPTY_XML

    def _callcenter_conf(self):
        return _EMPTY_XML
    
    def _acl_conf(self):
        _content = """
        <network-lists>
        <list name="lan" default="deny">
        </list>
        <list name="loopback.auto" default="allow">
        </list>
        <list name="localnet.auto" default="allow">
        </list>

        <list name="domains" default="deny">
        <node type="allow" domain="$${domain}"/>
        </list>
        </network-lists>
        """
        _ip = self._get_freeswitch_ip() or "$${domain}"
        _content = _content.replace("{{domain}}", _ip)

        _xml = _CONFIGURATION_XML_TEMPLATE % ("acl", "acl", _content)
        return _xml

    def _event_socket_conf(self):

        _password = self._get_freeswitch_password()
        if not _password:
            _logger.error("Not find freeswitch password")
            return _EMPTY_XML
        
        _content = """
        <settings>
        <param name="nat-map" value="false"/>
        <param name="listen-ip" value="::"/>
        <param name="listen-port" value="8021"/>
        <param name="password" value="%s"/>
        </settings>
        """
        _content = _content % _password
        _xml = _CONFIGURATION_XML_TEMPLATE % ("event_socket", "event_socket", _content)
        return _xml

    def _directory_user_template(self, sip_number, sip_password):
        _template = """
        <user id="{{user_extension}}">
        <params>
        <param name="password" value="{{user_extension_password}}"/>
        <param name="vm-password" value="{{user_extension_password}}"/>
        </params>
        <variables>
        <variable name="toll_allow" value="domestic,international,local"/>
        <variable name="accountcode" value="{{user_extension}}"/>
        <variable name="user_context" value="default"/>
        <variable name="effective_caller_id_name" value="{{user_extension}}"/>
        <variable name="effective_caller_id_number" value="{{user_extension}}"/>
        <variable name="outbound_caller_id_name" value="$${outbound_caller_name}"/>
        <variable name="outbound_caller_id_number" value="$${outbound_caller_id}"/>
        </variables>
        </user>
        """
        _template = _template.replace("{{user_extension}}", sip_number)
        _template = _template.replace("{{user_extension_password}}", sip_password)
        return _template

    def _directory_directory_template(self, domain, user_xml):
        _template = """
        <document type="freeswitch/xml">
        <section name="directory">
        <domain name="{{domain}}">
        <params>
        <param name="dial-string" value="{^^:sip_invite_domain=${dialed_domain}:presence_id=${dialed_user}@${dialed_domain}}${sofia_contact(*/${dialed_user}@${dialed_domain})},${verto_contact(${dialed_user}@${dialed_domain})}"/>
        <param name="jsonrpc-allowed-methods" value="verto"/>
        </params>

        <variables>
        <variable name="record_stereo" value="true"/>
        </variables>

        <groups>
        <group name="default">
        <users>
        {{user_element}}
        </users>
        </group>
        </groups>
        </domain>
        </section>
        </document>
        """
        _template = _template.replace("{{domain}}", domain)
        _template = _template.replace("{{user_element}}", user_xml)
        return _template
    
    def _directory_sip_auth(self):
        _user = http.request.params.get("sip_auth_username") or http.request.params.get("user")
        if not _user:
            _logger.error("no user %s" % http.request.params)
            return _EMPTY_XML
        _domain = http.request.params.get("domain") # sip_auth_realm
        if not _domain:
            _logger.error("no domain %s" % http.request.params)
            return _EMPTY_XML
        _res_users_model = http.request.env["res.users"].sudo()    
        _res_user = _res_users_model.search([("sip_number", "=", "%s" % _user)], limit=1)
        if not _res_user:
            _logger.error("Sip number: [%s] not bind user" % _user)
            return _EMPTY_XML
        _user_xml = self._directory_user_template(_user, _res_user.sip_password)
        _directory_xml = self._directory_directory_template(_domain, _user_xml)
        return _directory_xml
    
    @http.route('/freeswitch_xml_curl/configuration', type='http', auth='none', csrf=False)
    def configuration(self, *args, **kw):
        _logger.info("Configuration: [%s]" % http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("configuration"):
            return _EMPTY_XML

        if self._is_key_value("xml_cdr.conf"):
            return self._xml_cdr_conf()

        if self._is_key_value("sofia.conf"):
            return self._sofia_conf()

        if self._is_key_value("conference.conf"):
            return self._conference_conf()

        if self._is_key_value("callcenter.conf"):
            return self._callcenter_conf()

        if self._is_key_value("event_socket.conf"):
            return self._event_socket_conf()

        if self._is_key_value("acl.conf"):
            return self._acl_conf()

        if self._is_key_value("voicemail.conf"):
            return _EMPTY_XML

        if self._is_key_value("loopback.conf"):
            return _EMPTY_XML

        if self._is_key_value("post_load_modules.conf"):
            return _EMPTY_XML

        if self._is_key_value("post_load_switch.conf"):
            return _EMPTY_XML

        if self._is_key_value("local_stream.conf"):
            return _EMPTY_XML

        if self._is_key_value("shout.conf"):
            return _EMPTY_XML

        if self._is_key_value("sndfile.conf"):
            return _EMPTY_XML

        if self._is_key_value("opus.conf"):
            return _EMPTY_XML

        if self._is_key_value("spandsp.conf"):
            return _EMPTY_XML

        if self._is_key_value("amr.conf"):
            return _EMPTY_XML

        if self._is_key_value("httapi.conf"):
            return _EMPTY_XML

        if self._is_key_value("hash.conf"):
            return _EMPTY_XML

        if self._is_key_value("fifo.conf"):
            return _EMPTY_XML

        if self._is_key_value("db.conf"):
            return _EMPTY_XML

        _logger.error("Configuration [%s] is not recognized." % self._get_key_value())
        return _EMPTY_XML

    @http.route('/freeswitch_xml_curl/dialplan', type='http', auth='none', csrf=False)
    def dialplan(self):
        _logger.info(http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("dialplan"):
            return _EMPTY_XML

        return _EMPTY_XML

    @http.route('/freeswitch_xml_curl/directory', type='http', auth='none', csrf=False)
    def directory(self, *args, **kw):
        _logger.info("DIRECTORY XML CURL---> %s" % http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("directory"):
            return _EMPTY_XML

        if self._is_purpose_matched("gateways"):
            return _EMPTY_XML

        if self._is_purpose_matched("network-list"):
            return self._directory_network_list()

        if self._is_action_matched("sip_auth"):
            return self._directory_sip_auth()

        if self._is_action_matched("user_call"):
            return self._directory_sip_auth()

        if self._is_action_matched("message-count"):
            return _EMPTY_XML

        _logger.error(">>>>> DIRECTORY UNKNOWN request %s" % http.request.params)

        return _EMPTY_XML


    @http.route('/freeswitch_xml_cdr', type='http', auth='none', csrf=False)
    def xml_cdr(self, *args, **kw):
        _logger.info(http.request.params)
        return ""
