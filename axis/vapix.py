"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .errors import AxisException
from .param_cgi import URL_GET as param_url, Params
from .port_cgi import Ports
from .pwdgrp_cgi import URL_GET as pwdgrp_url, Users
from .utils import session_request

_LOGGER = logging.getLogger(__name__)


class Vapix:
    """Vapix parameter request."""

    def __init__(self, config) -> None:
        """Store local reference to device config."""
        self.config = config

        self.params = None
        self.ports = None
        self.users = None

    def initialize_params(self, preload_data=True) -> None:
        """Load device parameters and initialize parameter management.

        Preload data can be disabled to selectively load params afterwards.
        """
        params = ''
        if preload_data:
            params = self.request('get', param_url)

        self.params = Params(params, self.request)

    def initialize_ports(self) -> None:
        """Load IO port parameters for device."""
        if not self.params:
            self.initialize_params(preload_data=False)
            self.params.update_ports()

        self.ports = Ports(self.params, self.request)

    def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        users = self.request('get', pwdgrp_url)
        self.users = Users(users, self.request)

    def request(self, method, path, **kwargs):
        """Prepare HTTP request."""
        if method == 'get':
            session_method = self.config.session.get

        elif method == 'post':
            session_method = self.config.session.post

        else:
            raise AxisException

        url = self.config.url + path
        result = session_request(session_method, url, **kwargs)

        _LOGGER.debug("Response: %s from %s", result, self.config.host)

        return result
