"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging
from typing import TYPE_CHECKING, Callable

import httpx
from packaging import version
import xmltodict

from ..errors import PathNotFound, RequestError, Unauthorized, raise_error
from .interfaces.api_discovery import ApiDiscoveryHandler
from .interfaces.api_handler import ApiHandler
from .interfaces.applications import (
    APPLICATION_STATE_RUNNING,
    PARAM_CGI_VALUE as APPLICATIONS_MINIMUM_VERSION,
    Applications,
)
from .interfaces.applications.fence_guard import FenceGuard
from .interfaces.applications.loitering_guard import LoiteringGuard
from .interfaces.applications.motion_guard import MotionGuard
from .interfaces.applications.object_analytics import ObjectAnalytics
from .interfaces.applications.vmd4 import Vmd4
from .interfaces.basic_device_info import BasicDeviceInfoHandler
from .interfaces.event_instances import EventInstances
from .interfaces.light_control import LightHandler
from .interfaces.mqtt import MqttClientHandler
from .interfaces.param_cgi import Params
from .interfaces.pir_sensor_configuration import PirSensorConfigurationHandler
from .interfaces.port_cgi import Ports
from .interfaces.port_management import (
    API_DISCOVERY_ID as IO_PORT_MANAGEMENT_ID,
    IoPortManagement,
)
from .interfaces.ptz import PtzControl
from .interfaces.pwdgrp_cgi import Users
from .interfaces.stream_profiles import StreamProfilesHandler
from .interfaces.user_groups import UNKNOWN, UserGroups
from .interfaces.view_areas import ViewAreaHandler
from .models.api import ApiRequest, ApiRequest2

if TYPE_CHECKING:
    from ..device import AxisDevice
    from .models.api import ApiDataT

LOGGER = logging.getLogger(__name__)

TIME_OUT = 15


class Vapix:
    """Vapix parameter request."""

    def __init__(self, device: "AxisDevice") -> None:
        """Store local reference to device config."""
        self.device = device
        self.auth = httpx.DigestAuth(device.config.username, device.config.password)

        self.applications: Applications | None = None
        self.event_instances: EventInstances | None = None
        self.fence_guard: FenceGuard | None = None
        self.loitering_guard: LoiteringGuard | None = None
        self.motion_guard: MotionGuard | None = None
        self.object_analytics: ObjectAnalytics | None = None
        self.params: Params | None = None
        self.ports: IoPortManagement | Ports | None = None
        self.ptz: PtzControl | None = None
        self.user_groups: UserGroups | None = None
        self.users: Users | None = None
        self.vmd4: Vmd4 | None = None

        self.api_discovery: ApiDiscoveryHandler = ApiDiscoveryHandler(self)
        self.basic_device_info = BasicDeviceInfoHandler(self)
        self.light_control = LightHandler(self)
        self.mqtt = MqttClientHandler(self)
        self.pir_sensor_configuration = PirSensorConfigurationHandler(self)
        self.stream_profiles = StreamProfilesHandler(self)
        self.view_areas = ViewAreaHandler(self)

    @property
    def firmware_version(self) -> str:
        """Firmware version of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.version
        return self.params.firmware_version  # type: ignore[union-attr]

    @property
    def product_number(self) -> str:
        """Product number of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.prodnbr
        return self.params.prodnbr  # type: ignore[union-attr]

    @property
    def product_type(self) -> str:
        """Product type of device."""
        if self.basic_device_info.supported():
            return self.basic_device_info.prodtype
        return self.params.prodtype  # type: ignore[union-attr]

    @property
    def serial_number(self) -> str:
        """Device serial number."""
        if self.basic_device_info.supported():
            return self.basic_device_info.serialnumber
        return self.params.system_serialnumber  # type: ignore[union-attr]

    @property
    def access_rights(self) -> str:
        """Access rights with the account."""
        if self.user_groups:
            return self.user_groups.privileges
        return UNKNOWN

    @property
    def streaming_profiles(self) -> list:
        """List streaming profiles."""
        if self.stream_profiles.supported():
            return list(self.stream_profiles.values())
        return self.params.stream_profiles  # type: ignore[union-attr]

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

        tasks = []

        if IO_PORT_MANAGEMENT_ID in self.api_discovery:
            tasks.append(self._initialize_api_attribute(IoPortManagement, "ports"))

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
            self.light_control,
            self.mqtt,
            self.pir_sensor_configuration,
            self.stream_profiles,
            self.view_areas,
        )
        for api in apis:
            if not api.supported():
                continue
            tasks.append(do_api_request(api))

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Load data from param.cgi."""
        self.params = Params(self)

        tasks = []

        if preload_data:
            tasks.append(self.params.update())

        else:
            tasks.append(self.params.update_properties())
            tasks.append(self.params.update_ptz())

            if not self.basic_device_info.supported():
                tasks.append(self.params.update_brand())

            if not self.ports:
                tasks.append(self.params.update_ports())

            if not self.stream_profiles.supported():
                tasks.append(self.params.update_stream_profiles())

            if self.view_areas.supported():
                tasks.append(self.params.update_image())

        if tasks:
            await asyncio.gather(*tasks)

        if not self.light_control.supported() and self.params.light_control:
            try:
                await self.light_control.update()
            except Unauthorized:  # Probably a viewer account
                pass

        if not self.ports:
            self.ports = Ports(self)

        if not self.ptz and self.params.ptz:
            self.ptz = PtzControl(self)

    async def initialize_applications(self) -> None:
        """Load data for applications on device."""
        self.applications = Applications(self)
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
                app_class.name in self.applications  # type: ignore[attr-defined]
                and self.applications[app_class.name].status  # type: ignore[attr-defined]
                == APPLICATION_STATE_RUNNING
            ):
                tasks.append(self._initialize_api_attribute(app_class, app_attr))

        if tasks:
            await asyncio.gather(*tasks)

    async def initialize_event_instances(self) -> None:
        """Initialize event instances of what events are supported by the device."""
        await self._initialize_api_attribute(EventInstances, "event_instances")

    async def initialize_users(self) -> None:
        """Load device user data and initialize user management."""
        self.users = Users(self)
        try:
            await self.users.update()
        except Unauthorized:
            pass

    async def load_user_groups(self) -> None:
        """Load user groups to know the access rights of the user.

        If information is available from pwdgrp.cgi use that.
        """
        user_groups = ""
        if self.users and self.device.config.username in self.users:
            user = self.users[self.device.config.username]
            user_groups = (
                f"{user.name}\n"  # type: ignore[attr-defined]
                + ("admin " if user.admin else "")  # type: ignore[attr-defined]
                + ("operator " if user.operator else "")  # type: ignore[attr-defined]
                + ("viewer " if user.viewer else "")  # type: ignore[attr-defined]
                + ("ptz" if user.ptz else "")  # type: ignore[attr-defined]
            )

        self.user_groups = UserGroups(self)
        if not user_groups:
            try:
                await self.user_groups.update()
                return
            except PathNotFound:
                pass
        self.user_groups.process_raw(user_groups)

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
                method, url, auth=self.auth, timeout=TIME_OUT, **kwargs  # type: ignore [arg-type]
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
            raise RequestError("Connection error: {}".format(errc))

        except httpx.RequestError as err:
            LOGGER.debug("%s", err)
            raise RequestError("Unknown error: {}".format(err))

        return {}

    async def new_request(self, api_request: ApiRequest2) -> bytes:
        """Make a request to the device."""
        return await self.do_request(
            method=api_request.method,
            path=api_request.path,
            content=api_request.content,
        )

    async def do_request(
        self,
        method: str,
        path: str,
        content: bytes | None = None,
        params: str | None = None,
    ) -> bytes:
        """Make a request to the device."""
        url = self.device.config.url + path
        LOGGER.debug("%s, %s, %s, %s", method, url, content, params)

        try:
            response = await self.device.config.session.request(
                method,
                url,
                content=content,
                params=params,
                auth=self.auth,
                timeout=TIME_OUT,
            )

        except httpx.TimeoutException:
            raise RequestError("Timeout")

        except httpx.TransportError as errc:
            LOGGER.debug("%s", errc)
            raise RequestError("Connection error: {}".format(errc))

        except httpx.RequestError as err:
            LOGGER.debug("%s", err)
            raise RequestError("Unknown error: {}".format(err))

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
