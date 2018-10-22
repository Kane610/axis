"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .errors import RequestError, Unauthorized
from .utils import session_request

_LOGGER = logging.getLogger(__name__)

PARAM_URL = '{}://{}:{}/axis-cgi/{}?action={}&{}'


class Vapix(object):
    """Vapix parameter request."""

    def __init__(self, config):
        """Store local reference to device config."""
        self.config = config

    def get_param(self, param):
        """Get parameter and remove descriptive part of response."""
        cgi = 'param.cgi'
        action = 'list'
        result = self.do_request(cgi, action, 'group=' + param)

        if result is None:
            return None

        v = {}
        for s in filter(None, result.split('\n')):
            key, value = s.split('=')
            v[key] = value

        if len(v.items()) == 1:
            return v[param]

        return v

    def do_request(self, cgi, action, param):
        """Prepare HTTP request."""
        url = PARAM_URL.format(
            self.config.web_proto, self.config.host, self.config.port,
            cgi, action, param)

        result = session_request(self.config.session.get, url)
        _LOGGER.debug("Response: %s from %s", result, self.config.host)
        return result

        try:
            result = session_request(self.config.session.get, url)
            _LOGGER.debug("Response: %s from %s", result, self.config.host)
            return result

        except (RequestError, Unauthorized):
            _LOGGER.error("Couldn't get data from %s", self.config.host)
            return None

    @property
    def version(self):
        """Firmware version."""
        try:
            return self._version
        except AttributeError:
            self._version = self.get_param('Properties.Firmware.Version')
            return self._version

    @property
    def model(self):
        """Product model."""
        try:
            return self._model
        except AttributeError:
            self._model = self.get_param('Brand.ProdNbr')
            return self._model

    @property
    def serial_number(self):
        """Device MAC address."""
        try:
            return self._serial_number
        except AttributeError:
            self._serial_number = self.get_param(
                'Properties.System.SerialNumber')
            return self._serial_number

    @property
    def meta_data_support(self):
        """Yes if meta data stream is supported."""
        try:
            return self._meta_data_support
        except AttributeError:
            self._meta_data_support = self.get_param(
                'Properties.API.Metadata.Metadata')
            return self._meta_data_support
