"""Python library to enable Axis devices to integrate with Home Assistant."""

import requests
from requests.auth import HTTPDigestAuth

class Configuration(object):
    """Device configuration."""

    def __init__(self, *,
                 loop, host, username, password,
                 port=80, web_proto='http', verify_ssl=False,
                 event_types=None, signal=None):
        """All config params available to the device."""
        self.loop = loop
        self.web_proto = web_proto
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(
            self.username, self.password)
        if self.web_proto == 'https':
            self.session.verify_ssl = verify_ssl

        self.event_types = event_types
        self.signal = signal
