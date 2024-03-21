"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import httpx

from ..errors import RequestError, raise_error
from .interfaces.api_discovery import ApiDiscoveryHandler
from .interfaces.api_handler import ApiHandler
from .interfaces.applications import (
    ApplicationsHandler,
)
from .interfaces.applications.fence_guard import FenceGuardHandler
from .interfaces.applications.loitering_guard import (
    LoiteringGuardHandler,
)
from .interfaces.applications.motion_guard import MotionGuardHandler
from .interfaces.applications.object_analytics import (
    ObjectAnalyticsHandler,
)
from .interfaces.applications.vmd4 import Vmd4Handler
from .interfaces.basic_device_info import BasicDeviceInfoHandler
from .interfaces.event_instances import EventInstanceHandler
from .interfaces.light_control import LightHandler
from .interfaces.mqtt import MqttClientHandler
from .interfaces.parameters.param_cgi import Params
from .interfaces.pir_sensor_configuration import PirSensorConfigurationHandler
from .interfaces.port_cgi import Ports
from .interfaces.port_management import IoPortManagement
from .interfaces.ptz import PtzControl
from .interfaces.pwdgrp_cgi import Users
from .interfaces.stream_profiles import StreamProfilesHandler
from .interfaces.user_groups import UserGroups
from .interfaces.view_areas import ViewAreaHandler
from .models.api import ApiRequest
from .models.pwdgrp_cgi import SecondaryGroup
from .models.stream_profile import StreamProfile

if TYPE_CHECKING:
    from ..device import AxisDevice

LOGGER = logging.getLogger(__name__)

TIME_OUT = 15


class Vapix:
    """Vapix parameter request."""

    def __init__(self, device: "AxisDevice") -> None:
        """Store local reference to device config."""
        self.device = device
        self.auth = httpx.DigestAuth(device.config.username, device.config.password)

        self.users = Users(self)
        self.user_groups = UserGroups(self)

        self.api_discovery: ApiDiscoveryHandler = ApiDiscoveryHandler(self)
        self.params: Params = Params(self)

        self.basic_device_info = BasicDeviceInfoHandler(self)
        self.io_port_management = IoPortManagement(self)
        self.light_control = LightHandler(self)
        self.mqtt = MqttClientHandler(self)
        self.pir_sensor_configuration = PirSensorConfigurationHandler(self)
        self.stream_profiles = StreamProfilesHandler(self)
        self.view_areas = ViewAreaHandler(self)

        self.port_cgi = Ports(self)
        self.ptz = PtzControl(self)

        self.applications: ApplicationsHandler = ApplicationsHandler(self)
        self.fence_guard = FenceGuardHandler(self)
        self.loitering_guard = LoiteringGuardHandler(self)
        self.motion_guard = MotionGuardHandler(self)
        self.object_analytics = ObjectAnalyticsHandler(self)
        self.vmd4 = Vmd4Handler(self)

        self.event_instances = EventInstanceHandler(self)

    @property
    def firmware_version(self) -> str:
        """Firmware version of device."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].firmware_version
        if self.params.property_handler.initialized:
            return self.params.property_handler["0"].firmware_version
        return ""

    @property
    def product_number(self) -> str:
        """Product number of device."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].product_number
        if self.params.brand_handler.initialized:
            return self.params.brand_handler["0"].product_number
        return ""

    @property
    def product_type(self) -> str:
        """Product type of device."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].product_type
        if self.params.brand_handler.initialized:
            return self.params.brand_handler["0"].product_type
        return ""

    @property
    def serial_number(self) -> str:
        """Device serial number."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].serial_number
        if self.params.property_handler.initialized:
            return self.params.property_handler["0"].system_serial_number
        return ""

    @property
    def access_rights(self) -> SecondaryGroup:
        """Access rights with the account."""
        if user := self.user_groups.get("0"):
            return user.privileges
        return SecondaryGroup.UNKNOWN

    @property
    def streaming_profiles(self) -> list[StreamProfile]:
        """List streaming profiles."""
        if self.stream_profiles.initialized:
            return list(self.stream_profiles.values())
        if self.params.stream_profile_handler.initialized:
            return self.params.stream_profile_handler["0"].stream_profiles
        return []

    @property
    def ports(self) -> IoPortManagement | Ports:
        """Temporary port property."""
        if self.io_port_management.supported:
            return self.io_port_management
        return self.port_cgi

    async def initialize(self) -> None:
        """Initialize Vapix functions."""
        await self.initialize_api_discovery()
        await self.initialize_param_cgi(preload_data=False)
        await self.initialize_applications()

    async def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        if not await self.api_discovery.update():
            return

        apis: tuple[ApiHandler[Any], ...] = (
            self.basic_device_info,
            self.io_port_management,
            self.light_control,
            self.mqtt,
            self.pir_sensor_configuration,
            self.stream_profiles,
            self.view_areas,
        )
        await asyncio.gather(*[api.update() for api in apis if api.supported])

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        tasks = []

        if preload_data:
            tasks.append(self.params.update())

        else:
            tasks.append(self.params.property_handler.update())

            if (
                not self.basic_device_info.supported
                or not self.basic_device_info.initialized
            ):
                tasks.append(self.params.brand_handler.update())

            if not self.io_port_management.supported:
                tasks.append(self.params.io_port_handler.update())

            if not self.stream_profiles.supported:
                tasks.append(self.params.stream_profile_handler.update())

            if self.view_areas.supported:
                tasks.append(self.params.image_handler.update())

        await asyncio.gather(*tasks)

        if not self.params.property_handler.supported:
            return

        if (
            not self.light_control.listed_in_api_discovery
            and self.light_control.listed_in_parameters
        ):
            await self.light_control.update()

        if not self.io_port_management.supported and self.port_cgi.supported:
            self.port_cgi.load_ports()

        if self.params.property_handler["0"].ptz:
            await self.params.ptz_handler.update()

    async def initialize_applications(self) -> None:
        """Load data for applications on device."""
        if not self.applications.supported or not await self.applications.update():
            return

        apps: tuple[ApiHandler[Any], ...] = (
            self.fence_guard,
            self.loitering_guard,
            self.motion_guard,
            self.object_analytics,
            self.vmd4,
        )
        await asyncio.gather(*[app.update() for app in apps if app.supported])

    async def initialize_event_instances(self) -> None:
        """Initialize event instances of what events are supported by the device."""
        await self.event_instances.update()

    async def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        await self.users.update()

    async def load_user_groups(self) -> None:
        """Load user groups to know the access rights of the user.

        If information is available from pwdgrp.cgi use that.
        """
        user_groups = {}
        if len(self.users) > 0 and self.device.config.username in self.users:
            user_groups = {"0": self.users[self.device.config.username]}

        if not user_groups and await self.user_groups.update():
            return
        self.user_groups._items.update(user_groups)

    async def api_request(self, api_request: ApiRequest) -> bytes:
        """Make a request to the device."""
        return await self.request(
            method=api_request.method,
            path=api_request.path,
            content=api_request.content,
            data=api_request.data,
            headers=api_request.headers,
            params=api_request.params,
        )

    async def request(
        self,
        method: str,
        path: str,
        content: bytes | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> bytes:
        """Make a request to the device."""
        url = self.device.config.url + path
        LOGGER.debug("%s, %s, '%s', '%s', '%s'", method, url, content, data, params)

        try:
            response = await self.device.config.session.request(
                method,
                url,
                content=content,
                data=data,
                headers=headers,
                params=params,
                auth=self.auth,
                timeout=TIME_OUT,
            )

        except httpx.TimeoutException:
            raise RequestError("Timeout")

        except httpx.TransportError as errc:
            LOGGER.debug("%s", errc)
            raise RequestError(f"Connection error: {errc}")

        except httpx.RequestError as err:
            LOGGER.debug("%s", err)
            raise RequestError(f"Unknown error: {err}")

        try:
            response.raise_for_status()

        except httpx.HTTPStatusError as errh:
            LOGGER.debug("%s, %s", response, errh)
            raise_error(response.status_code)

        LOGGER.debug(
            "Response (from %s %s): %s",
            self.device.config.host,
            path,
            response.content,
        )

        return response.content
