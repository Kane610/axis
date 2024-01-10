"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
from collections.abc import Callable
import logging
from typing import TYPE_CHECKING

import httpx
import xmltodict

from ..errors import PathNotFound, RequestError, Unauthorized, raise_error
from .interfaces.api_discovery import ApiDiscoveryHandler
from .interfaces.api_handler import ApiHandler
from .interfaces.applications import (
    ApplicationsHandler,
)
from .interfaces.applications.fence_guard import FenceGuardHandler
from .interfaces.applications.loitering_guard import (
    LoiteringGuardHandler,
)
from .interfaces.applications.motion_guard import MotionGuard
from .interfaces.applications.object_analytics import (
    ObjectAnalyticsHandler,
)
from .interfaces.applications.vmd4 import Vmd4Handler
from .interfaces.basic_device_info import BasicDeviceInfoHandler
from .interfaces.event_instances import EventInstances
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
from .models.applications.application import ApplicationStatus
from .models.pwdgrp_cgi import SecondaryGroup

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

        self.event_instances: EventInstances | None = None
        self.motion_guard: MotionGuard | None = None

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
        self.object_analytics = ObjectAnalyticsHandler(self)
        self.vmd4 = Vmd4Handler(self)

    @property
    def firmware_version(self) -> str:
        """Firmware version of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.version
        if self.params.property_handler.supported():
            return self.params.property_handler.get_params()["0"].firmware_version
        return ""

    @property
    def product_number(self) -> str:
        """Product number of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.prodnbr
        if self.params.brand_handler.supported():
            return self.params.brand_handler.get_params()["0"].prodnbr
        return ""

    @property
    def product_type(self) -> str:
        """Product type of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.prodtype
        if self.params.brand_handler.supported():
            return self.params.brand_handler.get_params()["0"].prodtype
        return ""

    @property
    def serial_number(self) -> str:
        """Device serial number."""
        if self.basic_device_info.supported():
            return self.basic_device_info.serialnumber
        if self.params.property_handler.supported():
            return self.params.property_handler.get_params()["0"].system_serialnumber
        return ""

    @property
    def access_rights(self) -> SecondaryGroup:
        """Access rights with the account."""
        if user := self.user_groups.get("0"):
            return user.privileges
        return SecondaryGroup.UNKNOWN

    @property
    def streaming_profiles(self) -> list:
        """List streaming profiles."""
        if self.stream_profiles.supported():
            return list(self.stream_profiles.values())
        if self.params.stream_profile_handler.supported():
            return self.params.stream_profile_handler.get_params()["0"].stream_profiles
        return []

    @property
    def ports(self) -> IoPortManagement | Ports:
        """Temporary port property."""
        if not self.io_port_management.supported():
            return self.port_cgi
        return self.io_port_management

    async def initialize(self) -> None:
        """Initialize Vapix functions."""
        await self.initialize_api_discovery()
        await self.initialize_param_cgi(preload_data=False)
        await self.initialize_applications()

    async def _initialize_api_attribute(
        self, api_class: Callable, api_attr: str
    ) -> None:
        """Initialize API and load data."""
        api_instance = api_class(self)
        try:
            await api_instance.update()
        except Unauthorized:  # Probably a viewer account
            pass
        else:
            setattr(self, api_attr, api_instance)

    async def initialize_api_discovery(self) -> None:
        """Load API list from API Discovery."""
        try:
            await self.api_discovery.update()
        except PathNotFound:  # Device doesn't support API discovery
            return

        async def do_api_request(api: ApiHandler) -> None:
            """Try update of API."""
            try:
                await api.update()
            except Unauthorized:  # Probably a viewer account
                pass
            except NotImplementedError:
                pass

        apis: tuple[ApiHandler, ...] = (
            self.basic_device_info,
            self.io_port_management,
            self.light_control,
            self.mqtt,
            self.pir_sensor_configuration,
            self.stream_profiles,
            self.view_areas,
        )

        tasks = []

        for api in apis:
            if not api.supported():
                continue
            tasks.append(do_api_request(api))

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        tasks = []

        if preload_data:
            tasks.append(self.params.update())

        else:
            tasks.append(self.params.property_handler.update())
            tasks.append(self.params.ptz_handler.update())

            if not self.basic_device_info.supported():
                tasks.append(self.params.brand_handler.update())

            if not self.io_port_management.supported():
                tasks.append(self.params.io_port_handler.update())

            if not self.stream_profiles.supported():
                tasks.append(self.params.stream_profile_handler.update())

            if self.view_areas.supported():
                tasks.append(self.params.image_handler.update())

        await asyncio.gather(*tasks)

        if not self.params.property_handler.supported():
            return

        if (
            not self.light_control.supported()
            and self.params.property_handler["0"].light_control
        ):
            try:
                await self.light_control.update()
            except Unauthorized:  # Probably a viewer account
                pass

        if not self.io_port_management.supported():
            self.port_cgi.load_ports()

    async def initialize_applications(self) -> None:
        """Load data for applications on device."""

        async def do_api_request(api: ApiHandler) -> bool:
            """Try update of API."""
            if not api.supported():
                return False
            try:
                await api.update()
            except Unauthorized:  # Probably a viewer account
                pass
            return api.initialized

        if not await do_api_request(self.applications):
            return

        tasks = []

        for app_class, app_attr in ((MotionGuard, "motion_guard"),):
            if (
                app_class.name in self.applications
                and self.applications[app_class.name].status
                == ApplicationStatus.RUNNING
            ):
                tasks.append(self._initialize_api_attribute(app_class, app_attr))

        for app in (
            self.fence_guard,
            self.loitering_guard,
            self.object_analytics,
            self.vmd4,
        ):
            tasks.append(do_api_request(app))  # type: ignore [arg-type]

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_event_instances(self) -> None:
        """Initialize event instances of what events are supported by the device."""
        await self._initialize_api_attribute(EventInstances, "event_instances")

    async def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        try:
            await self.users.update()
        except Unauthorized:
            pass

    async def load_user_groups(self) -> None:
        """Load user groups to know the access rights of the user.

        If information is available from pwdgrp.cgi use that.
        """
        user_groups = {}
        if len(self.users) > 0 and self.device.config.username in self.users:
            user_groups = {"0": self.users[self.device.config.username]}

        if not user_groups:
            try:
                await self.user_groups.update()
                return
            except PathNotFound:
                pass
        self.user_groups._items = user_groups

    async def request(
        self,
        method: str,
        path: str,
        kwargs_xmltodict: dict | None = None,
        **kwargs: dict,
    ) -> dict | str:
        """Make a request to the API."""
        url = self.device.config.url + path

        LOGGER.debug("%s %s", url, kwargs)
        try:
            response = await self.device.config.session.request(
                method,
                url,
                auth=self.auth,
                timeout=TIME_OUT,
                **kwargs,  # type: ignore [arg-type]
            )
            response.raise_for_status()

            LOGGER.debug("Response: %s from %s", response.text, self.device.config.host)

            content_type = response.headers.get("Content-Type", "").split(";")[0]

            if content_type == "application/json":
                result = response.json()
                if "error" in result:
                    return {}
                return result

            if content_type in ["text/xml", "application/soap+xml"]:
                return xmltodict.parse(response.text, **(kwargs_xmltodict or {}))

            if response.text.startswith("# Error:"):
                return ""
            return response.text

        except httpx.HTTPStatusError as errh:
            LOGGER.debug("%s, %s", response, errh)
            raise_error(response.status_code)

        except httpx.TimeoutException:
            raise RequestError("Timeout")

        except httpx.TransportError as errc:
            LOGGER.debug("%s", errc)
            raise RequestError(f"Connection error: {errc}")

        except httpx.RequestError as err:
            LOGGER.debug("%s", err)
            raise RequestError(f"Unknown error: {err}")

        return {}

    async def new_request(self, api_request: ApiRequest) -> bytes:
        """Make a request to the device."""
        return await self.do_request(
            method=api_request.method,
            path=api_request.path,
            content=api_request.content,
            data=api_request.data,
            params=api_request.params,
        )

    async def do_request(
        self,
        method: str,
        path: str,
        content: bytes | None = None,
        data: dict[str, str] | None = None,
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

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(
                "Response: %s from %s %s",
                response.content,
                self.device.config.host,
                path,
            )

        return response.content
