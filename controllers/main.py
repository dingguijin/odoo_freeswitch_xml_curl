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
        if http.request.params.get("tag_name") != name:
            return False
        return True

    def _is_hostname_matched(self):

        _freeswitch_hostname = "freeswitch_hostname"

        _model = http.request.env["freeswitch_xml_curl.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)

        # _sss = _model.search([("is_active", '=', True)], limit=1)

        # _logger.info(_ss)
        # _logger.info(len(_ss))

        # _logger.info(_ss[0])
        # _logger.info(_ss[0].get("freeswitch_hostname"))

        # _logger.info(len(_sss))
        #_logger.info(_sss)
        # _logger.info(_sss.freeswitch_hostname)

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
        
    def _sofia_conf(self):
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

<list name="domains" default="deny">
<node type="allow" domain="$${domain}"/>
</list>
</network-lists>
"""
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

    @http.route('/freeswitch_xml_curl/configuration', type='http', auth='none', csrf=False)
    def configuration(self, *args, **kw):
        logging.info(http.request.params)

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

        _logger.info("%s is not recognized." % self._get_key_value())
        return _EMPTY_XML

    @http.route('/freeswitch_xml_curl/dialplan', type='http', auth='none', csrf=False)
    def dialplan(self):
        logging.info(http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("dialplan"):
            return _EMPTY_XML

        return _EMPTY_XML

    @http.route('/freeswitch_xml_curl/directory', type='http', auth='none', csrf=False)
    def directory(self, *args, **kw):
        logging.info(http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("directory"):
            return _EMPTY_XML

        return _EMPTY_XML


    @http.route('/freeswitch_xml_cdr', type='http', auth='none', csrf=False)
    def directory(self, *args, **kw):
        logging.info(http.request.params)
        return ""
