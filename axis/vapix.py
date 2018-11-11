"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .errors import RequestError, Unauthorized
from .utils import session_request

_LOGGER = logging.getLogger(__name__)

PARAM_URL = '{}://{}:{}/axis-cgi/{}?action={}&{}'

# Param.cgi
VAPIX_FW_VERSION = ('param.cgi', 'list', 'Properties.Firmware.Version')
VAPIX_IMAGE_FORMAT = ('param.cgi', 'list', 'Properties.Image.Format')
VAPIX_MDNS_FRIENDLY_NAME = (
    'param.cgi', 'list', 'Network.Bonjour.FriendlyName')
VAPIX_META_DATA_SUPPORT = (
    'param.cgi', 'list', 'Properties.API.Metadata.Metadata')
VAPIX_MODEL_ID = ('param.cgi', 'list', 'Brand.ProdNbr')
VAPIX_PROD_TYPE = ('param.cgi', 'list', 'Brand.ProdType')
VAPIX_SERIAL_NUMBER = ('param.cgi', 'list', 'Properties.System.SerialNumber')

# Pwdgrp.cgi
VAPIX_USER_LIST = ('pwdgrp.cgi', 'get', '')


class Vapix(object):
    """Vapix parameter request."""

    def __init__(self, config):
        """Store local reference to device config."""
        self.config = config

    def get(self, vapix_tuple):
        """"""
        cgi, action, param = vapix_tuple

        if cgi == 'param.cgi':
            group_param = 'group=' + param

        result = self.do_request(cgi, action, group_param)

        parameters = {
            key: value
            for s in filter(None, result.split('\n'))
            for key, value in [s.split('=')]
        }

        if param in parameters:
            return parameters[param]
        return parameters

    def do_request(self, cgi, action, param):
        """Prepare HTTP request."""
        url = PARAM_URL.format(
            self.config.web_proto, self.config.host, self.config.port,
            cgi, action, param)

        try:
            result = session_request(self.config.session.get, url)
            _LOGGER.debug("Response: %s from %s", result, self.config.host)
            return result

        except (RequestError, Unauthorized):
            _LOGGER.error("Couldn't get data from %s", self.config.host)
            return None
