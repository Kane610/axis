"""Python library to enable Axis devices to integrate with Home Assistant."""

import json
import logging

from .api_discovery import ApiDiscovery
from .basic_device_info import BasicDeviceInfo, API_DISCOVERY_ID as BASIC_DEVICE_INFO_ID
from .errors import AxisException, PathNotFound
from .mqtt import MqttClient, API_DISCOVERY_ID as MQTT_ID
from .param_cgi import URL_GET as PARAM_URL, Params
from .port_management import IoPortManagement, API_DISCOVERY_ID as IO_PORT_MANAGEMENT_ID
from .port_cgi import Ports
from .pwdgrp_cgi import URL_GET as PWDGRP_URL, Users
from .utils import session_request

LOGGER = logging.getLogger(__name__)


class Vapix:
    """Vapix parameter request."""

    def __init__(self, config) -> None:
        """Store local reference to device config."""
        self.config = config

        self.api_discovery = None
        self.basic_device_info = None
        self.mqtt = None
        self.params = None
        self.ports = None
        self.users = None

    @property
    def firmware_version(self):
        """Firmware version of device."""
        if self.basic_device_info:
            return self.basic_device_info.version
        return self.params.firmware_version

    @property
    def product_number(self):
        """Product number of device."""
        if self.basic_device_info:
            return self.basic_device_info.prodnbr
        return self.params.prodnbr

    @property
    def product_type(self):
        """Product type of device."""
        if self.basic_device_info:
            return self.basic_device_info.prodtype
        return self.params.prodtype

    @property
    def serial_number(self):
        """Serial number of device."""
        if self.basic_device_info:
            return self.basic_device_info.serialnumber
        return self.params.system_serialnumber

    def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        self.api_discovery = ApiDiscovery({}, self.json_request)
        self.api_discovery.update()

        if BASIC_DEVICE_INFO_ID in self.api_discovery:
            self.basic_device_info = BasicDeviceInfo({}, self.json_request)
            self.basic_device_info.update()

        if IO_PORT_MANAGEMENT_ID in self.api_discovery:
            self.ports = IoPortManagement({}, self.json_request)
            self.ports.update()

        if MQTT_ID in self.api_discovery:
            self.mqtt = MqttClient({}, self.json_request)

    def initialize_params(self, preload_data=True) -> None:
        """Load device parameters and initialize parameter management.

        Preload data can be disabled to selectively load params afterwards.
        """
        params = ""
        if preload_data:
            params = self.request("get", PARAM_URL)

        self.params = Params(params, self.request)

    def initialize_ports(self) -> None:
        """Load IO port parameters for device."""
        if self.ports:
            return

        if not self.params:
            self.initialize_params(preload_data=False)
            self.params.update_ports()

        self.ports = Ports(self.params, self.request)

    def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        users = self.request("get", PWDGRP_URL)
        self.users = Users(users, self.request)

    def request(self, method, path, **kwargs):
        """Prepare HTTP request."""
        if method == "get":
            session_method = self.config.session.get

        elif method == "post":
            session_method = self.config.session.post

        else:
            raise AxisException

        url = self.config.url + path
        result = session_request(session_method, url, **kwargs)

        LOGGER.debug("Response: %s from %s", result, self.config.host)

        if result.startswith("# Error:"):
            result = ""

        return result

    def json_request(self, method, path: str, **kwargs) -> dict:
        """Prepare JSON request."""
        if method == "get":
            session_method = self.config.session.get

        elif method == "post":
            session_method = self.config.session.post

        else:
            raise AxisException

        url = self.config.url + path
        try:
            result = session_request(session_method, url, **kwargs)
        except PathNotFound:
            return {}

        LOGGER.debug("Response: %s from %s", result, self.config.host)

        json_result = json.loads(result)
        if "error" in json_result:
            json_result = {}

        return json_result
