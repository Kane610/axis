"""Models for listing installed apps and licenses through the VAPIX Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from dataclasses import dataclass
import enum
import logging
import re
from typing import Literal, NotRequired, Self, TypedDict

import xmltodict

from ...errors import ResponseError
from ..api import ApiItem, ApiRequest, ApiResponse, BytesResponse

LOGGER = logging.getLogger(__name__)


class ApplicationControlError(ResponseError):
    """A device explicitly rejected an application control request."""

    def __init__(self, code: int) -> None:
        """Store the numeric device error without exposing response content."""
        self.code = code
        super().__init__(f"Application control error {code}")


class ApplicationObjectT(TypedDict):
    """Application details returned by the Application API list endpoint."""

    ApplicationID: NotRequired[str]
    Bundled: NotRequired[str]
    CompatibleOsVersions: NotRequired[object]
    ConfigurationPage: NotRequired[str]
    LicenseName: NotRequired[str]
    License: NotRequired[str]
    LicenseExpirationDate: NotRequired[str]
    Name: str
    NiceName: NotRequired[str]
    Resources: NotRequired[object]
    SignatureStatus: NotRequired[str]
    SignedStatus: NotRequired[str]
    Status: NotRequired[str]
    ValidationResult: NotRequired[str]
    Vendor: NotRequired[str]
    VendorHomePage: NotRequired[str]
    Version: NotRequired[str]


class ListApplicationReplyDataT(TypedDict):
    """Application list result and any returned application entries."""

    application: NotRequired[list[ApplicationObjectT]]
    result: Literal["ok", "error"]


class ListApplicationDataT(TypedDict):
    """XML reply node containing the application-list result and entries."""

    reply: NotRequired[ListApplicationReplyDataT]


class ApplicationName(enum.StrEnum):
    """Known Axis analytics application identifiers."""

    FENCE_GUARD = "fenceguard"
    LOITERING_GUARD = "loiteringguard"
    MOTION_GUARD = "motionguard"
    OBJECT_ANALYTICS = "objectanalytics"
    VMD4 = "vmd"


class ApplicationLicense(enum.StrEnum):
    """License state reported for an installed application."""

    VALID = "Valid"
    INVALID = "Invalid"
    MISSING = "Missing"
    CUSTOM = "Custom"
    NONE = "None"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        """Treat unrecognized device license values as unknown."""
        LOGGER.debug("Unknown application license status.")
        return cls.UNKNOWN


class ApplicationStatus(enum.StrEnum):
    """Run state reported for an installed application."""

    RUNNING = "Running"
    STOPPED = "Stopped"
    IDLE = "Idle"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        """Treat unrecognized device application states as unknown."""
        LOGGER.debug("Unknown application status.")
        return cls.UNKNOWN


@dataclass(frozen=True)
class Application(ApiItem):
    """Installed application metadata, including license and run state."""

    application_id: str | None
    """Application identifier supplied by the device, when available."""

    configuration_page: str | None
    """Relative URL to application configuration page."""

    license_name: str
    """License name."""

    license_status: ApplicationLicense
    """License status of application.

    License status:
        Valid = License is installed and valid.
        Invalid = License is installed but not valid.
        Missing = No license is installed.
        Custom = Custom license is used. License status cannot be retrieved.
        None = Application does not require any license.
    """

    license_expiration_date: str
    """Date (YYYY-MM-DD) when the license expires."""

    name: str
    """Application's machine-readable name."""

    nice_name: str
    """Application's display name."""

    status: ApplicationStatus
    """Status of application.

    Application status:
        Running = Application is running.
        Stopped = Application is not running.
        Idle = Application is idle.
    """

    validation_result_page: str
    """Validation result or page reference returned by the device."""

    vendor: str
    """Company that publishes the application."""

    vendor_page: str
    """Vendor's homepage URL, when provided by the device."""

    version: str
    """Version of application."""

    bundled: str | None = None
    signature_status: str | None = None
    resources: tuple[dict[str, str], ...] = ()
    compatible_os_versions: tuple[dict[str, str], ...] = ()

    @classmethod
    def decode(cls, data: ApplicationObjectT) -> Self:
        """Convert an Application API list entry to an application model."""
        return cls(
            id=data["Name"],
            application_id=data.get("ApplicationID"),
            configuration_page=data.get("ConfigurationPage"),
            license_name=data.get("LicenseName", ""),
            license_status=ApplicationLicense(data.get("License", "")),
            license_expiration_date=data.get("LicenseExpirationDate", ""),
            name=data["Name"],
            nice_name=data.get("NiceName", ""),
            status=ApplicationStatus(data.get("Status", "")),
            validation_result_page=data.get("ValidationResult", ""),
            vendor=data.get("Vendor", ""),
            vendor_page=data.get("VendorHomePage", ""),
            version=data.get("Version", ""),
            bundled=data.get("Bundled"),
            signature_status=data.get("SignatureStatus", data.get("SignedStatus")),
            resources=_application_details(
                data.get("Resources"), "Resource", ("name", "used")
            ),
            compatible_os_versions=_application_details(
                data.get("CompatibleOsVersions"), "VersionRange", ("Min", "Max")
            ),
        )


def _application_details(
    container: object, element: str, keys: tuple[str, str]
) -> tuple[dict[str, str], ...]:
    if container is None:
        return ()
    if not isinstance(container, dict):
        msg = "Invalid application details."
        raise ResponseError(msg)
    entries = container.get(element, [])
    if not isinstance(entries, list):
        entries = [entries]
    if any(not isinstance(entry, dict) for entry in entries):
        msg = "Invalid application details."
        raise ResponseError(msg)
    return tuple(
        {key: value for key in keys if isinstance(value := entry.get(key), str)}
        for entry in entries
    )


@dataclass
class ListApplicationsResponse(ApiResponse[dict[str, Application]]):
    """Installed applications indexed by their names."""

    data: dict[str, Application]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the XML application list and index its entries by name."""
        data = xmltodict.parse(bytes_data, attr_prefix="", force_list={"application"})
        if not isinstance(data, dict) or not isinstance(data.get("reply"), dict):
            msg = "Invalid application list response."
            raise ResponseError(msg)
        reply = data["reply"]
        if reply.get("result") != "ok":
            msg = "Application list request failed."
            raise ResponseError(msg)
        apps: list[ApplicationObjectT] = reply.get("application", [])
        return cls(data=Application.decode_to_dict(apps))


@dataclass
class ListApplicationsRequest(ApiRequest[ListApplicationsResponse]):
    """Request the list of applications installed on the device."""

    method = "post"
    path = "/axis-cgi/applications/list.cgi"
    content_type = "text/xml"
    response_type = ListApplicationsResponse


@dataclass
class ControlApplicationRequest(ApiRequest[BytesResponse]):
    """Start, stop, restart, or remove an application."""

    method = "post"
    path = "/axis-cgi/applications/control.cgi"
    content_type = "text/plain"
    response_type = BytesResponse

    action: Literal["start", "stop", "restart", "remove"]
    package: str

    @property
    def params(self) -> dict[str, str]:
        """Encode the selected action and package as query parameters."""
        return {"action": self.action, "package": self.package}


@dataclass
class ApplicationInfoResponse(ApiResponse[list[str]]):
    """Supported ACAP SDKs reported by the device."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the supported SDK list without treating failures as empty results."""
        data = xmltodict.parse(bytes_data, attr_prefix="", force_list={"sdk"})
        reply = data.get("reply") if isinstance(data, dict) else None
        if not isinstance(reply, dict) or reply.get("result") != "ok":
            msg = "Application information request failed."
            raise ResponseError(msg)
        supported = reply.get("supportedSdks")
        if supported is None and "supportedSdks" in reply:
            return cls(data=[])
        if not isinstance(supported, dict):
            msg = "Invalid application information response."
            raise ResponseError(msg)
        sdks = supported.get("sdk", [])
        if not isinstance(sdks, list) or not all(isinstance(sdk, str) for sdk in sdks):
            msg = "Invalid application SDK list."
            raise ResponseError(msg)
        return cls(data=sdks)


@dataclass
class ApplicationInfoRequest(ApiRequest[ApplicationInfoResponse]):
    """Request general application platform information."""

    method = "post"
    path = "/axis-cgi/applications/info.cgi"
    content_type = "text/xml"
    response_type = ApplicationInfoResponse


@dataclass
class ApplicationConfigResponse(ApiResponse[bool]):
    """Device policy governing unsigned application installation."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the actual policy value returned by the device."""
        data = xmltodict.parse(bytes_data, attr_prefix="")
        reply = data.get("reply") if isinstance(data, dict) else None
        param = reply.get("param") if isinstance(reply, dict) else None
        if (
            not isinstance(reply, dict)
            or reply.get("result") != "ok"
            or not isinstance(param, dict)
            or param.get("name") != "AllowUnsigned"
            or param.get("value") not in ("true", "false")
        ):
            msg = "Invalid application policy response."
            raise ResponseError(msg)
        return cls(data=param["value"] == "true")


@dataclass
class ApplicationConfigRequest(ApiRequest[ApplicationConfigResponse]):
    """Read the AllowUnsigned application policy."""

    method = "post"
    path = "/axis-cgi/applications/config.cgi"
    content_type = "text/xml"
    response_type = ApplicationConfigResponse

    @property
    def params(self) -> dict[str, str]:
        """Specify the policy being read."""
        return {"action": "get", "name": "AllowUnsigned"}


@dataclass
class SetApplicationConfigRequest(ApiRequest[ApplicationConfigResponse]):
    """Set the AllowUnsigned application policy."""

    method = "post"
    path = "/axis-cgi/applications/config.cgi"
    content_type = "text/xml"
    response_type = ApplicationConfigResponse
    allow_unsigned: bool

    @property
    def params(self) -> dict[str, str]:
        """Specify the requested policy."""
        return {
            "action": "set",
            "name": "AllowUnsigned",
            "value": str(self.allow_unsigned).lower(),
        }


@dataclass
class RemoveApplicationLicenseRequest(ApiRequest[BytesResponse]):
    """Remove an application's license key."""

    method = "post"
    path = "/axis-cgi/applications/license.cgi"
    content_type = "text/plain"
    response_type = BytesResponse
    package: str

    @property
    def params(self) -> dict[str, str]:
        """Specify the target application."""
        return {"action": "removelicensekey", "package": self.package}


def validate_control_response(content: bytes) -> None:
    """Accept only a documented success and report device error codes."""
    content = content.strip()
    if content == b"OK":
        return
    if match := re.fullmatch(rb"Error:\s*(\d{1,3})", content):
        raise ApplicationControlError(int(match[1]))
    msg = "Invalid application control response."
    raise ResponseError(msg)
