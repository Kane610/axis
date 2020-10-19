"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
from packaging import version

import httpx

from .api_discovery import ApiDiscovery
from .applications import (
    APPLICATION_STATE_RUNNING,
    Applications,
    PARAM_CGI_KEY as APPLICATIONS_PARAM,
    PARAM_CGI_VALUE as APPLICATIONS_MINIMUM_VERSION,
)
from .applications.fence_guard import FenceGuard
from .applications.loitering_guard import LoiteringGuard
from .applications.motion_guard import MotionGuard
from .applications.vmd4 import Vmd4
from .basic_device_info import BasicDeviceInfo, API_DISCOVERY_ID as BASIC_DEVICE_INFO_ID
from .configuration import Configuration
from .errors import raise_error, PathNotFound, RequestError, Unauthorized
from .light_control import LightControl, API_DISCOVERY_ID as LIGHT_CONTROL_ID
from .mqtt import MqttClient, API_DISCOVERY_ID as MQTT_ID
from .param_cgi import Params
from .port_management import IoPortManagement, API_DISCOVERY_ID as IO_PORT_MANAGEMENT_ID
from .port_cgi import Ports
from .pwdgrp_cgi import URL_GET as PWDGRP_URL, Users
from .stream_profiles import StreamProfiles, API_DISCOVERY_ID as STREAM_PROFILES_ID

LOGGER = logging.getLogger(__name__)


class Vapix:
    """Vapix parameter request."""

    def __init__(self, config: Configuration) -> None:
        """Store local reference to device config."""
        self.config = config
        self.session = httpx.AsyncClient(
            auth=httpx.DigestAuth(config.username, config.password),
            verify=config.verify_ssl,
        )

        self.api_discovery = None
        self.applications = None
        self.basic_device_info = None
        self.fence_guard = None
        self.light_control = None
        self.loitering_guard = None
        self.motion_guard = None
        self.mqtt = None
        self.params = None
        self.ports = None
        self.stream_profiles = None
        self.users = None
        self.vmd4 = None

    async def close(self):
        """Close session."""
        if self.session:
            await self.session.aclose()
            self.session = None

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

    async def initialize(self) -> None:
        """Initialize Vapix functions."""
        await self.initialize_api_discovery()
        await self.initialize_param_cgi(preload_data=False)
        await self.initialize_applications()

    async def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        self.api_discovery = ApiDiscovery(self.request)
        try:
            await self.api_discovery.update()
        except PathNotFound:  # Device doesn't support API discovery
            return

        for api_id, api_class, api_attr in (
            (BASIC_DEVICE_INFO_ID, BasicDeviceInfo, "basic_device_info"),
            (IO_PORT_MANAGEMENT_ID, IoPortManagement, "ports"),
            (LIGHT_CONTROL_ID, LightControl, "light_control"),
            (MQTT_ID, MqttClient, "mqtt"),
            (STREAM_PROFILES_ID, StreamProfiles, "stream_profiles"),
        ):
            if api_id in self.api_discovery:
                try:
                    api_item = api_class(self.request)
                    await api_item.update()
                    setattr(self, api_attr, api_item)
                except Unauthorized:  # Probably a viewer account
                    pass

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        self.params = Params(self.request)

        if preload_data:
            await self.params.update()

        if not preload_data:
            await self.params.update_properties()

            if not self.basic_device_info:
                await self.params.update_brand()

            if not self.ports:
                await self.params.update_ports()

            if not self.stream_profiles:
                await self.params.update_stream_profiles()

        if not self.light_control and self.params.light_control:
            try:
                light_control = LightControl(self.request)
                await light_control.update()
                self.light_control = light_control
            except Unauthorized:  # Probably a viewer account
                pass

        if not self.ports:
            self.ports = Ports(self.params, self.request)

    async def initialize_applications(self):
        """Load data for applications on device."""
        self.applications = Applications(self.request)
        if (
            self.params
            and f"root.{APPLICATIONS_PARAM}" in self.params
            and version.parse(self.params.embedded_development)
            >= version.parse(APPLICATIONS_MINIMUM_VERSION)
        ):
            try:
                await self.applications.update()
            except Unauthorized:  # Probably a viewer account
                return

        for app_class, app_attr in (
            (FenceGuard, "fence_guard"),
            (LoiteringGuard, "loitering_guard"),
            (MotionGuard, "motion_guard"),
            (Vmd4, "vmd4"),
        ):
            if app_class.APPLICATION_NAME not in self.applications:
                continue

            app_item = app_class(self.request)

            if (
                self.applications[app_class.APPLICATION_NAME].status
                != APPLICATION_STATE_RUNNING
            ):
                continue

            await app_item.update()
            setattr(self, app_attr, app_item)

    async def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        users = await self.request("get", PWDGRP_URL)
        self.users = Users(users, self.request)

    async def request(self, method: str, path: str, **kwargs: dict) -> str:
        """Make a request to the API."""
        url = self.config.url + path

        LOGGER.debug("%s %s", url, kwargs)

        try:
            response = await self.session.request(method, url, **kwargs)
            response.raise_for_status()

            LOGGER.debug("Response: %s from %s", response.text, self.config.host)

            if "application/json" in response.headers.get("Content-Type"):
                result = response.json()
                if "error" in result:
                    return {}
                return result

            if response.text.startswith("# Error:"):
                return ""
            return response.text

        except httpx.HTTPStatusError as errh:
            LOGGER.debug("%s, %s", response, errh)
            raise_error(response.status_code)

        except httpx.TimeoutException as errt:
            LOGGER.debug("%s", errt)
            raise RequestError("Timeout: {}".format(errt))

        except httpx.TransportError as errc:
            LOGGER.debug("%s", errc)
            raise RequestError("Connection error: {}".format(errc))

        except httpx.RequestError as err:
            LOGGER.debug("%s", err)
            raise RequestError("Unknown error: {}".format(err))
