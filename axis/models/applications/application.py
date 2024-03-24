"""Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from dataclasses import dataclass
import enum
from typing import Literal, NotRequired, Self, TypedDict

import xmltodict

from ..api import ApiItem, ApiRequest, ApiResponse


class ApplicationObjectT(TypedDict):
    """Application object description."""

    ApplicationID: str
    ConfigurationPage: str
    LicenseName: NotRequired[str]
    License: Literal["Valid", "Invalid", "Missing", "Custom", "None"]
    LicenseExpirationDate: NotRequired[str]
    Name: str
    NiceName: str
    Status: Literal["Running", "Stopped", "Idle"]
    ValidationResult: NotRequired[str]
    Vendor: str
    VendorHomePage: NotRequired[str]
    Version: str


class ListApplicationReplyDataT(TypedDict):
    """List applications response."""

    application: NotRequired[list[ApplicationObjectT]]
    result: Literal["ok", "error"]


class ListApplicationDataT(TypedDict):
    """List of applications root data."""

    reply: NotRequired[ListApplicationReplyDataT]


class ApplicationName(enum.StrEnum):
    """Application name."""

    FENCE_GUARD = "fenceguard"
    LOITERING_GUARD = "loiteringguard"
    MOTION_GUARD = "motionguard"
    OBJECT_ANALYTICS = "objectanalytics"
    VMD4 = "vmd"


class ApplicationLicense(enum.StrEnum):
    """Application license."""

    VALID = "Valid"
    INVALID = "Invalid"
    MISSING = "Missing"
    CUSTOM = "Custom"
    NONE = "None"


class ApplicationStatus(enum.StrEnum):
    """Application license."""

    RUNNING = "Running"
    STOPPED = "Stopped"
    IDLE = "Idle"


@dataclass(frozen=True)
class Application(ApiItem):
    """Representation of an Application instance."""

    application_id: str | None
    """Id of application."""

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
    """Name of application."""

    nice_name: str
    """Name of application."""

    status: ApplicationStatus
    """Status of application.

    Application status:
        Running = Application is running.
        Stopped = Application is not running.
        Idle = Application is idle.
    """

    validation_result_page: str
    """Complete URL to a validation or result page."""

    vendor: str
    """Vendor of application."""

    vendor_page: str
    """Vendor of application."""

    version: str
    """Version of application."""

    @classmethod
    def decode(cls, data: ApplicationObjectT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=data["Name"],
            application_id=data.get("ApplicationID"),
            configuration_page=data.get("ConfigurationPage"),
            license_name=data.get("LicenseName", ""),
            license_status=ApplicationLicense(data["License"]),
            license_expiration_date=data.get("LicenseExpirationDate", ""),
            name=data["Name"],
            nice_name=data["NiceName"],
            status=ApplicationStatus(data["Status"]),
            validation_result_page=data.get("ValidationResult", ""),
            vendor=data["Vendor"],
            vendor_page=data.get("VendorHomePage", ""),
            version=data["Version"],
        )


@dataclass
class ListApplicationsRequest(ApiRequest):
    """Request object for listing installed applications."""

    method = "post"
    path = "/axis-cgi/applications/list.cgi"
    content_type = "text/xml"


@dataclass
class ListApplicationsResponse(ApiResponse[dict[str, Application]]):
    """Response object for listing all applications."""

    data: dict[str, Application]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data = xmltodict.parse(bytes_data, attr_prefix="", force_list={"application"})
        apps: list[ApplicationObjectT] = data.get("reply", {}).get("application", [])
        return cls(data=Application.decode_to_dict(apps))
