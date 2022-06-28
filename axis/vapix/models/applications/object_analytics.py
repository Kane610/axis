"""Object Analytics API data model."""

from typing import Optional

from .api import ApplicationAPIItem


class ObjectAnalyticsScenario(ApplicationAPIItem):
    """Object Analytics Scenario."""

    @property
    def camera(self) -> list:  # type: ignore[override]
        """Camera ID."""
        return self.raw["devices"]

    @property
    def object_classifications(self) -> list:
        """Classifications of objects to detect."""
        return self.raw["objectClassifications"]

    @property
    def perspectives(self) -> Optional[list]:
        """Perspectives for improve triggers based on heights."""
        return self.raw.get("perspectives")

    @property
    def presets(self) -> list:
        """Presets."""
        return self.raw["presets"]

    @property
    def trigger_type(self) -> str:
        """Type of trigger."""
        return self.raw["type"]

    @property
    def uid(self) -> int:
        """Scenario ID."""
        return self.raw["id"]
