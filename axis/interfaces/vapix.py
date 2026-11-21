"""Manage one device's VAPIX API handlers and send requests through its HTTP session."""

import asyncio
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any, Literal

import aiohttp

from ..errors import AxisException, RequestError, ResponseError, raise_error
from ..models.configuration import AuthScheme
from ..models.pwdgrp_cgi import SecondaryGroup
from .api_discovery import ApiDiscoveryHandler
from .api_handler import ApiHandler, HandlerGroup
from .applications import ApplicationsHandler
from .applications.application_handler import ApplicationHandler
from .applications.fence_guard import FenceGuardHandler
from .applications.loitering_guard import LoiteringGuardHandler
from .applications.motion_guard import MotionGuardHandler
from .applications.object_analytics import ObjectAnalyticsHandler
from .applications.vmd4 import Vmd4Handler
from .basic_device_info import BasicDeviceInfoHandler
from .event_instances import EventInstanceHandler
from .firmware_management import FirmwareManagementHandler
from .light_control import LightHandler
from .mqtt import MqttClientHandler
from .parameters.param_cgi import Params
from .pir_sensor_configuration import PirSensorConfigurationHandler
from .port_cgi import Ports
from .port_management import IoPortManagement
from .ptz import PtzControl
from .pwdgrp_cgi import Users
from .restart_cgi import RestartHandler
from .stream_profiles import StreamProfilesHandler
from .temperature_control import TemperatureControlHandler
from .user_groups import UserGroups
from .view_areas import ViewAreaHandler
from .virtual_input import VirtualInputHandler

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from yarl import URL

    from ..device import AxisDevice
    from ..models.api import ApiRequest
    from ..models.stream_profile import StreamProfile

LOGGER = logging.getLogger(__name__)

TIME_OUT = 15


class UploadDigestError(ResponseError):
    """The device requires digest authentication that cannot stream a package."""


class _StreamingDigestAuthMiddleware(aiohttp.DigestAuthMiddleware):
    """Avoid aiohttp's full-body buffering for multipart digest authentication."""

    async def _encode(
        self, method: str, url: URL, body: aiohttp.payload.Payload | Literal[b""]
    ) -> str:
        if isinstance(body, aiohttp.MultipartWriter):
            qops = {qop.strip() for qop in self._challenge.get("qop", "").split(",")}
            if "auth-int" in qops:
                if "auth" not in qops:
                    msg = "Digest auth-int cannot stream an application package."
                    raise UploadDigestError(msg)
                self._challenge["qop"] = "auth"
        return await super()._encode(method, url, body)


class InterfaceInspectionError(AxisException):
    """Identify a failed interface probe without including device data."""

    def __init__(self, interface: str, cause: Exception) -> None:
        """Store the name of the interface that could not be inspected."""
        self.interface = interface
        self.cause = cause
        super().__init__(interface)


@dataclass(frozen=True)
class InterfaceState:
    """Availability and loaded-data status for one library handler.

    The CLI and other consumers should render this state directly instead of
    guessing API availability from a separate set of rules.
    """

    name: str
    api_id: str
    api_version: str
    listed: bool
    probe_attempted: bool
    probe_succeeded: bool
    supported: bool
    initialized: bool
    items: int


class Vapix:
    """Provide device API handlers, initialize supported features, and send HTTP requests."""

    auth: str | None

    def __init__(self, device: AxisDevice) -> None:
        """Set up authentication and API handlers without contacting the device."""
        self.device = device
        self._aiohttp_digest_middleware: Any | None = None

        if device.config.auth_scheme == AuthScheme.BASIC:
            self.auth = self._basic_auth_header()
        else:
            self.auth = None
            self._aiohttp_digest_middleware = self._aiohttp_digest_middleware_obj()

        # Grouped handlers are registered in handler-construction order.
        # Handlers with empty handler_groups are intentionally excluded.
        self._handler_registry: dict[HandlerGroup, list[ApiHandler[Any]]] = {
            group: [] for group in HandlerGroup
        }

        self.users = Users(self)
        self.user_groups = UserGroups(self)

        self.api_discovery: ApiDiscoveryHandler = ApiDiscoveryHandler(self)
        self.params: Params = Params(self)

        self.basic_device_info = BasicDeviceInfoHandler(self)
        self.firmware_management = FirmwareManagementHandler(self)
        self.io_port_management = IoPortManagement(self)
        self.light_control = LightHandler(self)
        self.mqtt = MqttClientHandler(self)
        self.pir_sensor_configuration = PirSensorConfigurationHandler(self)
        self.temperature_control = TemperatureControlHandler(self)
        self.stream_profiles = StreamProfilesHandler(self)
        self.view_areas = ViewAreaHandler(self)

        self.port_cgi = Ports(self)
        self.ptz = PtzControl(self)
        self.restart_cgi = RestartHandler(self)
        self.virtual_input = VirtualInputHandler(self)

        self.applications: ApplicationsHandler = ApplicationsHandler(self)
        self.fence_guard = FenceGuardHandler(self)
        self.loitering_guard = LoiteringGuardHandler(self)
        self.motion_guard = MotionGuardHandler(self)
        self.object_analytics = ObjectAnalyticsHandler(self)
        self.vmd4 = Vmd4Handler(self)

        self.event_instances = EventInstanceHandler(self)

    @property
    def firmware_version(self) -> str:
        """Return the firmware version from already loaded device data."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].firmware_version
        if self.params.property_handler.initialized:
            return self.params.property_handler["0"].firmware_version
        return ""

    @property
    def product_full_name(self) -> str:
        """Return the full product name from already loaded device data."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].product_full_name
        if self.params.brand_handler.initialized:
            return self.params.brand_handler["0"].product_full_name
        return ""

    @property
    def product_number(self) -> str:
        """Return the product number from already loaded device data."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].product_number
        if self.params.brand_handler.initialized:
            return self.params.brand_handler["0"].product_number
        return ""

    @property
    def product_type(self) -> str:
        """Return the product type from already loaded device data."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].product_type
        if self.params.brand_handler.initialized:
            return self.params.brand_handler["0"].product_type
        return ""

    @property
    def serial_number(self) -> str:
        """Return the serial number from already loaded device data."""
        if self.basic_device_info.initialized:
            return self.basic_device_info["0"].serial_number
        if self.params.property_handler.initialized:
            return self.params.property_handler["0"].system_serial_number
        return ""

    @property
    def access_rights(self) -> SecondaryGroup:
        """Return the logged-in account's cached privileges, or UNKNOWN if not loaded."""
        if user := self.user_groups.get("0"):
            return user.privileges
        return SecondaryGroup.UNKNOWN

    @property
    def streaming_profiles(self) -> list[StreamProfile]:
        """Return cached video-stream profiles, falling back to parameter data."""
        if self.stream_profiles.initialized:
            return list(self.stream_profiles.values())
        if self.params.stream_profile_handler.initialized:
            return self.params.stream_profile_handler["0"].stream_profiles
        return []

    @property
    def ports(self) -> IoPortManagement | Ports:
        """Use the newer I/O API when supported, otherwise the older port.cgi handler."""
        if self.io_port_management.supported:
            return self.io_port_management
        return self.port_cgi

    async def initialize(self) -> None:
        """Discover device APIs, load fallback parameters, and initialize applications."""
        await self.initialize_api_discovery()
        await self.initialize_param_cgi(preload_data=False)
        if "Companion" in self.product_full_name:
            self.device.config.is_companion = True
        await self.initialize_applications()

    async def initialize_api_discovery(self) -> None:
        """Read advertised APIs and initialize handlers in the discovery phase."""
        if not await self.api_discovery.update():
            return

        await self._initialize_handlers(HandlerGroup.API_DISCOVERY)

    def _register_handler(self, handler: ApiHandler[Any]) -> None:
        """Register a handler for grouped initialization.

        Registration order is the effective initialization order for each group.
        Handlers with empty ``handler_groups`` remain excluded by design.
        """
        for group in handler.handler_groups:
            if handler not in self._handler_registry[group]:
                self._handler_registry[group].append(handler)

    def _handlers_by_group(self, group: HandlerGroup) -> tuple[ApiHandler[Any], ...]:
        """Return handlers assigned to an initialization group."""
        return tuple(self._handler_registry[group])

    def interfaces(self) -> dict[str, ApiHandler[Any]]:
        """Return all Vapix interface handlers mapped by attribute name.

        This is a read-only discovery helper and does not trigger initialization
        or network requests.
        """
        return {
            name: value
            for name, value in vars(self).items()
            if isinstance(value, ApiHandler)
        }

    async def inspect_interfaces(
        self,
        *,
        refresh_discovery: bool = True,
        probe: bool = False,
    ) -> dict[str, InterfaceState]:
        """Report each handler's availability and loaded data, optionally testing its endpoint.

        Args:
            refresh_discovery: Refresh API discovery before evaluation.
            probe: Best-effort update of non-initialized handlers to determine
                practical support and current item counts. Application handlers
                are probed only when their application is known to be running.

        """
        if refresh_discovery:
            await self._inspect_update("api_discovery", self.api_discovery)

        states: dict[str, InterfaceState] = {}
        for name, handler in sorted(self.interfaces().items()):
            try:
                listed = handler.supported
                probe_attempted = False
                probe_succeeded = False

                if (
                    probe
                    and not handler.initialized
                    and (
                        not isinstance(handler, ApplicationHandler)
                        or handler.listed_in_applications
                    )
                ):
                    probe_attempted = True
                    probe_succeeded = await handler.update()

                items = len(handler)
                initialized = handler.initialized
                supported = bool(listed or probe_succeeded or initialized or items > 0)
                states[name] = InterfaceState(
                    name=name,
                    api_id=str(getattr(handler.api_id, "value", "") or ""),
                    api_version=handler.api_version,
                    listed=listed,
                    probe_attempted=probe_attempted,
                    probe_succeeded=probe_succeeded,
                    supported=supported,
                    initialized=initialized,
                    items=items,
                )
            except (
                AxisException,
                AttributeError,
                LookupError,
                TypeError,
                ValueError,
            ) as err:
                raise InterfaceInspectionError(name, err) from err

        return states

    async def _inspect_update(self, name: str, handler: ApiHandler[Any]) -> bool:
        """Add safe context to an unsuccessful discovery or interface probe."""
        try:
            return await handler.update()
        except (
            AxisException,
            AttributeError,
            LookupError,
            TypeError,
            ValueError,
        ) as err:
            raise InterfaceInspectionError(name, err) from err

    async def _initialize_handlers(self, group: HandlerGroup) -> None:
        """Initialize handlers in a group."""
        handlers = self._handlers_by_group(group)
        await asyncio.gather(
            *[
                handler.update()
                for handler in handlers
                if handler.supported and handler.should_initialize_in_group(group)
            ]
        )

    async def initialize_param_cgi(self, preload_data: bool = True) -> None:
        """Read parameter groups and initialize handlers that use parameter-based support."""
        tasks: list[Awaitable[bool]] = []

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

        await self._initialize_handlers(HandlerGroup.PARAM_CGI_FALLBACK)

        if not self.io_port_management.supported and self.port_cgi.supported:
            self.port_cgi.load_ports()

        if self.params.property_handler["0"].ptz:
            await self.params.ptz_handler.update()

    async def initialize_applications(self) -> None:
        """Load data for applications on device."""
        if not self.applications.supported or not await self.applications.update():
            return

        await self._initialize_handlers(HandlerGroup.APPLICATION)

    async def initialize_event_instances(self) -> None:
        """Read the event sources and types supported by the device."""
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
        self.user_groups.update_items(user_groups)

    async def api_request[ApiResponseT](
        self,
        api_request: ApiRequest[ApiResponseT],
    ) -> ApiResponseT:
        """Send an API request and decode its bytes using the request's response type."""
        params = api_request.params or {}
        if self.device.config.is_companion and api_request.supports_companion_param:
            params["Axis-Orig-Sw"] = "true"
        bytes_data = await self.request(
            method=api_request.method,
            path=api_request.path,
            content=api_request.content,
            data=api_request.data,
            headers=api_request.headers,
            params=params,
        )

        decoder = api_request.response_type
        return decoder.decode(bytes_data)

    async def api_request_once[ApiResponseT](
        self, api_request: ApiRequest[ApiResponseT]
    ) -> ApiResponseT:
        """Send a write without redirects or automatic Basic authentication retries."""
        params = api_request.params or {}
        if self.device.config.is_companion and api_request.supports_companion_param:
            params["Axis-Orig-Sw"] = "true"
        status, _headers, content = await self._perform_request(
            method=api_request.method,
            url=self.device.config.url + api_request.path,
            content=api_request.content,
            data=api_request.data,
            headers=api_request.headers,
            params=params,
            allow_redirects=False,
        )
        if status >= 400:
            raise_error(status)
        if status >= 300:
            msg = "Unexpected device write redirect."
            raise ResponseError(msg)
        return api_request.response_type.decode(content)

    async def request(
        self,
        method: str,
        path: str,
        content: bytes | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> bytes:
        """Send an HTTP request to the device and return its response bytes."""
        return await self._request(
            method=method,
            path=path,
            content=content,
            data=data,
            headers=headers,
            params=params,
            allow_auto_basic_retry=True,
        )

    async def _request(
        self,
        method: str,
        path: str,
        content: bytes | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        allow_auto_basic_retry: bool = False,
    ) -> bytes:
        """Send an HTTP request, handle failures, and optionally retry with Basic authentication."""
        url = self.device.config.url + path
        LOGGER.debug("%s, %s, '%s', '%s', '%s'", method, url, content, data, params)

        try:
            (
                status_code,
                response_headers,
                response_content,
            ) = await self._perform_request(
                method=method,
                url=url,
                content=content,
                data=data,
                headers=headers,
                params=params,
            )

        except TimeoutError as errt:
            message = "Timeout"
            raise RequestError(message) from errt

        except Exception as err:
            if isinstance(err, aiohttp.ClientConnectionError):
                LOGGER.debug("%s", err)
                message = f"Connection error: {err}"
                raise RequestError(message) from err
            if isinstance(err, aiohttp.ClientError):
                LOGGER.debug("%s", err)
                message = f"Unknown error: {err}"
                raise RequestError(message) from err
            raise

        if status_code >= 400:
            if self._should_retry_with_basic(response_headers, allow_auto_basic_retry):
                self.auth = self._basic_auth_header()
                self._aiohttp_digest_middleware = None
                return await self._request(
                    method=method,
                    path=path,
                    content=content,
                    data=data,
                    headers=headers,
                    params=params,
                    allow_auto_basic_retry=False,
                )

            LOGGER.debug("status=%s headers=%s", status_code, response_headers)
            raise_error(status_code)

        LOGGER.debug(
            "Response (from %s %s): %s",
            self.device.config.host,
            path,
            response_content,
        )

        return response_content

    async def _perform_request(
        self,
        method: str,
        url: str,
        content: bytes | None,
        data: dict[str, str] | aiohttp.FormData | None,
        headers: dict[str, str] | None,
        params: dict[str, str] | None,
        *,
        request_timeout: float = TIME_OUT,
        allow_redirects: bool = True,
    ) -> tuple[int, dict[str, str], bytes]:
        """Execute request with the configured HTTP session."""
        request_data: bytes | dict[str, str] | aiohttp.FormData | None = (
            content if content is not None else data
        )
        session = self.device.config.session

        request_headers = dict(headers or {})
        if self.auth is not None and not any(
            header.lower() == "authorization" for header in request_headers
        ):
            request_headers["Authorization"] = self.auth

        request_kwargs: dict[str, Any] = {
            "data": request_data,
            "headers": request_headers,
            "params": params,
            "timeout": request_timeout,
        }
        if not allow_redirects:
            request_kwargs["allow_redirects"] = False
        if self._aiohttp_digest_middleware is not None:
            request_kwargs["middlewares"] = (self._aiohttp_digest_middleware,)

        async with session.request(method, url, **request_kwargs) as response:
            response_content = await response.read()
            return response.status, dict(response.headers), response_content

    async def upload_multipart(
        self,
        path: str,
        data: aiohttp.FormData,
        *,
        request_timeout: float,
        params: dict[str, str] | None = None,
    ) -> bytes:
        """Send one multipart request without redirect or automatic Basic retry."""
        status, _headers, content = await self._perform_request(
            method="post",
            url=self.device.config.url + path,
            content=None,
            data=data,
            headers=None,
            params=params,
            request_timeout=request_timeout,
            allow_redirects=False,
        )
        if status >= 400:
            raise_error(status)
        if status >= 300:
            msg = "Unexpected upload redirect."
            raise ResponseError(msg)
        return content

    def _aiohttp_digest_middleware_obj(self) -> Any | None:
        """Create aiohttp digest middleware when available and relevant."""
        if self.device.config.auth_scheme == AuthScheme.BASIC:
            return None

        middleware_cls = getattr(aiohttp, "DigestAuthMiddleware", None)
        if middleware_cls is None:
            LOGGER.debug("aiohttp DigestAuthMiddleware unavailable, digest disabled")
            return None

        return _StreamingDigestAuthMiddleware(
            login=self.device.config.username,
            password=self.device.config.password,
        )

    def _basic_auth_header(self) -> str:
        """Create an HTTP Basic Authorization header value."""
        return aiohttp.encode_basic_auth(
            self.device.config.username, self.device.config.password
        )

    def _should_retry_with_basic(
        self, headers: dict[str, str], allow_auto_basic_retry: bool
    ) -> bool:
        """Return if request should retry once with basic authentication."""
        if not allow_auto_basic_retry:
            return False

        if self.device.config.auth_scheme != AuthScheme.AUTO:
            return False

        expected_auth = ""
        for header_name, header_value in headers.items():
            if header_name.lower() == "www-authenticate":
                expected_auth = header_value.lower()
                break
        return "basic" in expected_auth
