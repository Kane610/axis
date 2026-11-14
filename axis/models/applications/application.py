"""Models for listing installed apps and licenses through the VAPIX Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from dataclasses import dataclass
import enum
from typing import Literal, NotRequired, Self, TypedDict

import xmltodict

from ..api import ApiItem, ApiRequest, ApiResponse


class ApplicationObjectT(TypedDict):
    """Application details returned by the Application API list endpoint."""

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


class ApplicationStatus(enum.StrEnum):
    """Run state reported for an installed application."""

    RUNNING = "Running"
    STOPPED = "Stopped"
    IDLE = "Idle"


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

    @classmethod
    def decode(cls, data: ApplicationObjectT) -> Self:
        """Convert an Application API list entry to an application model."""
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
class ListApplicationsResponse(ApiResponse[dict[str, Application]]):
    """Installed applications indexed by their names."""

    data: dict[str, Application]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the XML application list and index its entries by name."""
        data = xmltodict.parse(bytes_data, attr_prefix="", force_list={"application"})
        apps: list[ApplicationObjectT] = data.get("reply", {}).get("application", [])
        return cls(data=Application.decode_to_dict(apps))


@dataclass
class ListApplicationsRequest(ApiRequest[ListApplicationsResponse]):
    """Request the list of applications installed on the device."""

    method = "post"
    path = "/axis-cgi/applications/list.cgi"
    content_type = "text/xml"
    response_type = ListApplicationsResponse
