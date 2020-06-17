"""Python library to enable Axis devices to integrate with Home Assistant."""

import json
import logging

from .api_discovery import ApiDiscovery
from .basic_device_info import BasicDeviceInfo, API_DISCOVERY_ID as BASIC_DEVICE_INFO_ID
from .configuration import Configuration
from .errors import AxisException, PathNotFound, Unauthorized
from .light_control import LightControl, API_DISCOVERY_ID as LIGHT_CONTROL_ID
from .mqtt import MqttClient, API_DISCOVERY_ID as MQTT_ID
from .param_cgi import Params
from .port_management import IoPortManagement, API_DISCOVERY_ID as IO_PORT_MANAGEMENT_ID
from .port_cgi import Ports
from .pwdgrp_cgi import URL_GET as PWDGRP_URL, Users
from .stream_profiles import StreamProfiles, API_DISCOVERY_ID as STREAM_PROFILES_ID
from .utils import session_request

LOGGER = logging.getLogger(__name__)


class Vapix:
    """Vapix parameter request."""

    def __init__(self, config: Configuration) -> None:
        """Store local reference to device config."""
        self.config = config

        self.api_discovery = None
        self.basic_device_info = None
        self.light_control = None
        self.mqtt = None
        self.params = None
        self.ports = None
        self.stream_profiles = None
        self.users = None

    @property
    def firmware_version(self) -> str:
        """Firmware version of device."""
        if self.basic_device_info:
            return self.basic_device_info.version
        return self.params.firmware_version

    @property
    def product_number(self) -> str:
        """Product number of device."""
        if self.basic_device_info:
            return self.basic_device_info.prodnbr
        return self.params.prodnbr

    @property
    def product_type(self) -> str:
        """Product type of device."""
        if self.basic_device_info:
            return self.basic_device_info.prodtype
        return self.params.prodtype

    @property
    def serial_number(self) -> str:
        """Serial number of device."""
        if self.basic_device_info:
            return self.basic_device_info.serialnumber
        return self.params.system_serialnumber

    @property
    def streaming_profiles(self) -> list:
        """List streaming profiles."""
        if self.stream_profiles:
            return list(self.stream_profiles.values())
        return self.params.stream_profiles()

    def initialize(self) -> None:
        """Initialize Vapix functions."""
        self.initialize_api_discovery()
        self.initialize_param_cgi(preload_data=False)

    def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        self.api_discovery = ApiDiscovery(self.json_request)
        self.api_discovery.update()

        for api_id, api_class, api_attr in (
            (BASIC_DEVICE_INFO_ID, BasicDeviceInfo, "basic_device_info"),
            (IO_PORT_MANAGEMENT_ID, IoPortManagement, "ports"),
            (LIGHT_CONTROL_ID, LightControl, "light_control"),
            (MQTT_ID, MqttClient, "mqtt"),
            (STREAM_PROFILES_ID, StreamProfiles, "stream_profiles"),
        ):
            if api_id in self.api_discovery:
                try:
                    api_item = api_class(self.json_request)
                    api_item.update()
                    setattr(self, api_attr, api_item)
                except Unauthorized:
                    # Probably a viewer account
                    pass

    def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        self.params = Params(self.request)

        if preload_data:
            self.params.update()

        if not preload_data:
            self.params.update_properties()

            if not self.basic_device_info:
                self.params.update_brand()

            if not self.ports:
                self.params.update_ports()

            if not self.stream_profiles:
                self.params.update_stream_profiles()

        if not self.light_control and self.params.light_control:
            try:
                light_control = LightControl(self.json_request)
                light_control.update()
                self.light_control = light_control
            except Unauthorized:
                pass

        if not self.ports:
            self.ports = Ports(self.params, self.request)

    def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        users = self.request("get", PWDGRP_URL)
        self.users = Users(users, self.request)

    def request(self, method: str, path: str, **kwargs: dict) -> str:
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

    def json_request(self, method: str, path: str, **kwargs: dict) -> dict:
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
