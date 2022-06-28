"""Application API.

Use VAPIX® Application API to upload, control and manage applications and their license keys.
"""

from ..api import APIItem


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
