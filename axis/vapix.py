"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging
from packaging import version

import httpx
import xmltodict

from .api_discovery import ApiDiscovery
from .applications import (
    APPLICATION_STATE_RUNNING,
    Applications,
    PARAM_CGI_VALUE as APPLICATIONS_MINIMUM_VERSION,
)
from .applications.fence_guard import FenceGuard
from .applications.loitering_guard import LoiteringGuard
from .applications.motion_guard import MotionGuard
from .applications.object_analytics import ObjectAnalytics
from .applications.vmd4 import Vmd4
from .basic_device_info import BasicDeviceInfo, API_DISCOVERY_ID as BASIC_DEVICE_INFO_ID
from .configuration import Configuration
from .errors import raise_error, PathNotFound, RequestError, Unauthorized
from .light_control import LightControl, API_DISCOVERY_ID as LIGHT_CONTROL_ID
from .mqtt import MqttClient, API_DISCOVERY_ID as MQTT_ID
from .param_cgi import Params
from .port_management import IoPortManagement, API_DISCOVERY_ID as IO_PORT_MANAGEMENT_ID
from .port_cgi import Ports
from .ptz import PtzControl
from .pwdgrp_cgi import Users
from .stream_profiles import StreamProfiles, API_DISCOVERY_ID as STREAM_PROFILES_ID
from .view_areas import API_DISCOVERY_ID as VIEW_AREAS_ID, ViewAreas
from .user_groups import UNKNOWN, URL as USER_GROUPS_URL, UserGroups

LOGGER = logging.getLogger(__name__)


class Vapix:
    """Vapix parameter request."""

    def __init__(self, config: Configuration) -> None:
        """Store local reference to device config."""
        self.config = config
        self.auth = httpx.DigestAuth(self.config.username, self.config.password)

        self.api_discovery = None
        self.applications = None
        self.basic_device_info = None
        self.fence_guard = None
        self.light_control = None
        self.loitering_guard = None
        self.motion_guard = None
        self.mqtt = None
        self.object_analytics = None
        self.params = None
        self.ports = None
        self.ptz = None
        self.stream_profiles = None
        self.user_groups = None
        self.users = None
        self.view_areas = None
        self.vmd4 = None

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
    def access_rights(self) -> str:
        """Access rights with the account."""
        if self.user_groups:
            return self.user_groups.privileges
        return UNKNOWN

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

    async def _initialize_api_attribute(self, api_class: object, api_attr: str) -> None:
        """Initialize API and load data."""
        api_instance = api_class(self.request)
        try:
            await api_instance.update()
        except Unauthorized:  # Probably a viewer account
            pass
        else:
            setattr(self, api_attr, api_instance)

    async def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        self.api_discovery = ApiDiscovery(self.request)
        try:
            await self.api_discovery.update()
        except PathNotFound:  # Device doesn't support API discovery
            return

        tasks = []

        for api_id, api_class, api_attr in (
            (BASIC_DEVICE_INFO_ID, BasicDeviceInfo, "basic_device_info"),
            (IO_PORT_MANAGEMENT_ID, IoPortManagement, "ports"),
            (LIGHT_CONTROL_ID, LightControl, "light_control"),
            (MQTT_ID, MqttClient, "mqtt"),
            (STREAM_PROFILES_ID, StreamProfiles, "stream_profiles"),
            (VIEW_AREAS_ID, ViewAreas, "view_areas"),
        ):
            if api_id in self.api_discovery:
                tasks.append(self._initialize_api_attribute(api_class, api_attr))

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        self.params = Params(self.request)

        tasks = []

        if preload_data:
            tasks.append(self.params.update())

        else:
            tasks.append(self.params.update_properties())
            tasks.append(self.params.update_ptz())

            if not self.basic_device_info:
                tasks.append(self.params.update_brand())

            if not self.ports:
                tasks.append(self.params.update_ports())

            if not self.stream_profiles:
                tasks.append(self.params.update_stream_profiles())

            if self.view_areas:
                tasks.append(self.params.update_image())

        if tasks:
            await asyncio.gather(*tasks)

        if not self.light_control and self.params.light_control:
            await self._initialize_api_attribute(LightControl, "light_control")

        if not self.ports:
            self.ports = Ports(self.params, self.request)

        if not self.ptz and self.params.ptz:
            self.ptz = PtzControl(self.request)

    async def initialize_applications(self) -> None:
        """Load data for applications on device."""
        self.applications = Applications(self.request)
        if self.params and version.parse(
            self.params.embedded_development
        ) >= version.parse(APPLICATIONS_MINIMUM_VERSION):
            try:
                await self.applications.update()
            except Unauthorized:  # Probably a viewer account
                return

        tasks = []

        for app_class, app_attr in (
            (FenceGuard, "fence_guard"),
            (LoiteringGuard, "loitering_guard"),
            (MotionGuard, "motion_guard"),
            (ObjectAnalytics, "object_analytics"),
            (Vmd4, "vmd4"),
        ):
            if (
                app_class.APPLICATION_NAME in self.applications
                and self.applications[app_class.APPLICATION_NAME].status
                == APPLICATION_STATE_RUNNING
            ):
                tasks.append(self._initialize_api_attribute(app_class, app_attr))

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        self.users = Users("", self.request)
        try:
            await self.users.update()
        except Unauthorized:
            pass

    async def load_user_groups(self) -> None:
        """Load user groups to know the access rights of the user.

        If information is available from pwdgrp.cgi use that.
        """
        if self.users and self.config.username in self.users:
            user = self.users[self.config.username]
            user_groups = (
                f"{user.name}\n"
                + ("admin " if user.admin else "")
                + ("operator " if user.operator else "")
                + ("viewer " if user.viewer else "")
                + ("ptz" if user.ptz else "")
            )

        else:
            try:
                user_groups = await self.request("get", USER_GROUPS_URL)
            except PathNotFound:
                user_groups = ""

        self.user_groups = UserGroups(user_groups, self.request)

    async def request(self, method: str, path: str, **kwargs: dict) -> str:
        """Make a request to the API."""
        url = self.config.url + path

        LOGGER.debug("%s %s", url, kwargs)
        try:
            response = await self.config.session.request(
                method, url, auth=self.auth, **kwargs
            )
            response.raise_for_status()

            LOGGER.debug("Response: %s from %s", response.text, self.config.host)

            content_type = response.headers.get("Content-Type", "")

            if "application/json" in content_type:
                result = response.json()
                if "error" in result:
                    return {}
                return result

            if "text/xml" in content_type:
                return xmltodict.parse(response.text)

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
