"""Application API.

Use VAPIX® Application API to upload, control and manage applications and their license keys.
"""

from dataclasses import dataclass
from typing import Any, Self, TypedDict

import xmltodict

from ..api import APIItem, ApiItem, ApiRequest, ApiResponse


class Application(APIItem):
    """Application item."""

    @property
    def application_id(self) -> str:
        """Id of application."""
        return self.raw["@ApplicationID"]

    @property
    def configuration_page(self) -> str:
        """Relative URL to application configuration page."""
        return self.raw["@ConfigurationPage"]

    @property
    def license_name(self) -> str:
        """License name."""
        return self.raw.get("@LicenseName", "")

    @property
    def license_status(self) -> str:
        """License status of application.

        License status:
            Valid = License is installed and valid.
            Invalid = License is installed but not valid.
            Missing = No license is installed.
            Custom = Custom license is used. License status cannot be retrieved.
            None = Application does not require any license.
        """
        return self.raw["@License"]

    @property
    def license_expiration_date(self) -> str:
        """Date (YYYY-MM-DD) when the license expires."""
        return self.raw.get("@LicenseExpirationDate", "")

    @property
    def name(self) -> str:
        """Name of application."""
        return self.raw["@Name"]

    @property
    def nice_name(self) -> str:
        """Name of application."""
        return self.raw["@NiceName"]

    @property
    def status(self) -> str:
        """Status of application.

        Application status:
            Running = Application is running.
            Stopped = Application is not running.
            Idle = Application is idle.
        """
        return self.raw["@Status"]

    @property
    def validation_result_page(self) -> str:
        """Complete URL to a validation or result page."""
        return self.raw.get("@ValidationResult", "")

    @property
    def vendor(self) -> str:
        """Vendor of application."""
        return self.raw["@Vendor"]

    @property
    def vendor_page(self) -> str:
        """Vendor of application."""
        return self.raw["@VendorHomePage"]

    @property
    def version(self) -> str:
        """Version of application."""
        return self.raw["@Version"]


class ListApplicationReplyDataT(TypedDict):
    """List of API description data."""

    application: dict[str, Any]


class ListApplicationDataT(TypedDict):
    """List of applications data."""

    reply: ListApplicationReplyDataT


@dataclass
class App(ApiItem):
    """Representation of an Application instance."""

    application_id: str
    """Id of application."""

    configuration_page: str
    """Relative URL to application configuration page."""

    license_name: str
    """License name."""

    license_status: str
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

    status: str
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
    def decode(cls, data: Any) -> Self:
        """Decode dict to class object."""
        return cls(
            id=data["@Name"],
            application_id=data["@ApplicationID"],
            configuration_page=data["@ConfigurationPage"],
            license_name=data.get("@LicenseName", ""),
            license_status=data["@License"],
            license_expiration_date=data.get("@LicenseExpirationDate", ""),
            name=data["@Name"],
            nice_name=data["@NiceName"],
            status=data["@Status"],
            validation_result_page=data.get("@ValidationResult", ""),
            vendor=data["@Vendor"],
            vendor_page=data["@VendorHomePage"],
            version=data["@Version"],
        )

    @classmethod
    def decode_from_list(cls, data: ListApplicationReplyDataT) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        return {k: cls.decode(v) for k, v in data.items()}


@dataclass
class ListApplicationsRequest(ApiRequest):
    """Request object for listing installed applications."""

    method = "post"
    path = "/axis-cgi/applications/list.cgi"


@dataclass
class ListApplicationsResponse(ApiResponse[dict[str, App]]):
    """Response object for listing all applications."""

    data: dict[str, App]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        # xmltodict.parse(response.text, **(kwargs_xmltodict or {}))
        data = xmltodict.parse(bytes_data)
        return cls(
            data=App.decode_from_list(data["reply"]),
        )
