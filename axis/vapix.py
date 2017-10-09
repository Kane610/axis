import logging
import requests

from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth

_LOGGER = logging.getLogger(__name__)

PARAM_URL = 'http://{}:{}/axis-cgi/{}?action={}&{}'


class Vapix(object):
    """Vapix parameter request
    """

    def __init__(self, config):
        """Store local reference to device config
        """
        self.config = config

    def get_param(self, param):
        """Get parameter and remove descriptive part of response.
        """
        cgi = 'param.cgi'
        action = 'list'
        try:
            r = self.do_request(cgi, action, 'group=' + param)
        except requests.ConnectionError:
            return None
        except requests.exceptions.HTTPError:
            return None
        v = {}
        for s in filter(None, r.split('\n')):
            key, value = s.split('=')
            v[key] = value
        if len(v.items()) == 1:
            return v[param]
        else:
            return v

    def do_request(self, cgi, action, param):
        """Do HTTP request and return response as dictionary.
        """
        url = PARAM_URL.format(self.config.host,
                               self.config.port,
                               cgi,
                               action,
                               param)
        auth = HTTPDigestAuth(self.config.username, self.config.password)
        try:
            r = requests.get(url, auth=auth)
            r.raise_for_status()
        except requests.ConnectionError as err:
            _LOGGER.error("Connection error: %s", err)
            raise
        except requests.exceptions.HTTPError as err:
            _LOGGER.error("HTTP error: %s", err)
            raise
        _LOGGER.debug('Request response: %s from %s', r.text, self.config.host)
        return r.text


class Parameters(object):
    """Device parameters resolved upon request
    """

    @property
    def version(self):
        """Firmware version
        """
        if '_version' not in self.__dict__:
            self._version = self.vapix.get_param('Properties.Firmware.Version')
        return self._version

    @property
    def model(self):
        """Product model
        """
        if '_model' not in self.__dict__:
            self._model = self.vapix.get_param('Brand.ProdNbr')
        return self._model

    @property
    def serial_number(self):
        """Device MAC address
        """
        if '_serial_number' not in self.__dict__:
            self._serial_number = self.vapix.get_param('Properties.System.SerialNumber')
        return self._serial_number

    @property
    def meta_data_support(self):
        """Yes if meta data stream is supported
        """
        if '_meta_data_support' not in self.__dict__:
            self._meta_data_support = self.vapix.get_param('Properties.API.Metadata.Metadata')
        return self._meta_data_support
