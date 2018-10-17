"""Python library to enable Axis devices to integrate with Home Assistant."""

import requests
from requests.auth import HTTPDigestAuth

class Configuration(object):
    """Device configuration."""

    def __init__(self, loop, host, username, password, **kwargs):
        """All config params available to the device."""
        self.loop = loop
        self.web_proto = kwargs.get('web_proto', 'http')
        self.host = host
        self.port = kwargs.get('port', 80)
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(
            self.username, self.password)
        if self.web_proto == 'https':
            self.session.verify = False

        self.event_types = kwargs.get('events', None)
        self.signal = kwargs.get('signal', None)
        self.kwargs = kwargs
