"""Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from typing import IO, Literal

from aiohttp import FormData
from packaging import version

from ...models.applications.application import (
    Application,
    ApplicationConfigRequest,
    ApplicationInfoRequest,
    ControlApplicationRequest,
    ListApplicationsRequest,
    RemoveApplicationLicenseRequest,
    SetApplicationConfigRequest,
    validate_control_response,
)
from ..api_handler import ApiHandler

MINIMUM_VERSION = "1.20"
UPLOAD_PATH = "/axis-cgi/applications/upload.cgi"


class ApplicationsHandler(ApiHandler[Application]):
    """List applications installed on the device, such as video analytics."""

    @property
    def listed_in_parameters(self) -> bool:
        """Check whether device parameters report a supported application platform version."""
        if self.vapix.params.property_handler.supported and (
            properties := self.vapix.params.property_handler.get("0")
        ):
            return version.parse(properties.embedded_development) >= version.parse(
                MINIMUM_VERSION
            )
        return False

    async def _api_request(self) -> dict[str, Application]:
        """Read installed applications for this handler's cached data."""
        return await self.list_applications()

    async def list_applications(self) -> dict[str, Application]:
        """Read the applications installed on the device."""
        response = await self.vapix.api_request(ListApplicationsRequest())
        return response.data

    async def control_application(
        self, action: Literal["start", "stop", "restart", "remove"], package: str
    ) -> None:
        """Execute a single application action and validate the device response."""
        response = await self.vapix.api_request_once(
            ControlApplicationRequest(action, package)
        )
        validate_control_response(response.data)

    async def supported_sdks(self) -> list[str]:
        """Read the supported ACAP SDKs."""
        return (await self.vapix.api_request(ApplicationInfoRequest())).data

    async def allow_unsigned(self) -> bool:
        """Read whether unsigned application installation is enabled."""
        return (await self.vapix.api_request(ApplicationConfigRequest())).data

    async def set_allow_unsigned(self, value: bool) -> bool:
        """Set the unsigned application policy once."""
        response = await self.vapix.api_request_once(SetApplicationConfigRequest(value))
        return response.data

    async def remove_license(self, package: str) -> None:
        """Remove an application's license once."""
        response = await self.vapix.api_request_once(
            RemoveApplicationLicenseRequest(package)
        )
        validate_control_response(response.data)

    async def upload_license(self, package: str, license_file: IO[bytes]) -> None:
        """Upload a license key using the modern device web interface's form field."""
        data = FormData()
        data.add_field(
            "fileData", license_file, filename="license.xml", content_type="text/xml"
        )
        response = await self.vapix.upload_multipart(
            "/axis-cgi/applications/license.cgi",
            data,
            params={"action": "uploadlicensekey", "package": package},
            request_timeout=60,
        )
        validate_control_response(response)

    async def upload_application(self, package: IO[bytes]) -> None:
        """Upload a seekable ACAP package once and validate the device response."""
        data = FormData()
        data.add_field(
            "file",
            package,
            filename="application.eap",
            content_type="application/octet-stream",
        )
        response = await self.vapix.upload_multipart(
            UPLOAD_PATH, data, request_timeout=1800
        )
        validate_control_response(response)
