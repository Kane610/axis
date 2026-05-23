"""VAPIX temperature control support for Axis devices.

Defines models for the Axis VAPIX temperature control API, enabling integration and management of device temperature sensors, heaters, and fans via standardized endpoints.
Implements parsing, normalization, and status representation for temperature-related device features.
"""

from dataclasses import dataclass
import enum
import re
from typing import Self

from .api import ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"

_RUNNING_INTENSITY_RE = re.compile(r"Running\[(\d+)%?\]")


class TemperatureDeviceType(enum.StrEnum):
    """Temperature device category."""

    FAN = "fan"
    HEATER = "heater"
    SENSOR = "sensor"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> TemperatureDeviceType:
        """Map unsupported values to UNKNOWN."""
        return cls.UNKNOWN


class TemperatureDeviceStatus(enum.StrEnum):
    """Normalized state for fan/heater status strings."""

    FAILURE = "failure"
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> TemperatureDeviceStatus:
        """Map unsupported values to UNKNOWN."""
        return cls.UNKNOWN


@dataclass(frozen=True)
class TemperatureControlStatus(ApiItem):
    """Temperature status item from statusall response."""

    device_type: TemperatureDeviceType
    celsius: float | None = None
    fahrenheit: float | None = None
    intensity: int | None = None
    name: str | None = None
    status: TemperatureDeviceStatus = TemperatureDeviceStatus.UNKNOWN
    status_raw: str | None = None
    time_until_stop: int | None = None

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Create status object from parsed statusall key-value fields."""
        item_id = data["id"]
        status_raw = data.get("Status")
        status, intensity = _parse_status(status_raw)
        return cls(
            id=item_id,
            celsius=_to_float(data.get("Celsius")),
            device_type=TemperatureDeviceType(_device_type_from_id(item_id)),
            fahrenheit=_to_float(data.get("Fahrenheit")),
            intensity=intensity,
            name=data.get("Name"),
            status=status,
            status_raw=status_raw,
            time_until_stop=_to_int(data.get("TimeUntilStop")),
        )


@dataclass
class GetStatusAllResponse(ApiResponse[dict[str, TemperatureControlStatus]]):
    """Response object for temperature statusall."""

    data: dict[str, TemperatureControlStatus]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Decode statusall text payload to typed temperature objects."""
        text_data = bytes_data.decode("utf-8", errors="replace")
        parsed = _parse_statusall_entries(text_data)
        return cls(
            data={
                item_id: TemperatureControlStatus.decode({"id": item_id, **fields})
                for item_id, fields in parsed.items()
            }
        )


@dataclass
class GetStatusAllRequest(ApiRequest[GetStatusAllResponse]):
    """Request object for temperature statusall."""

    method = "get"
    path = "/axis-cgi/temperaturecontrol.cgi"
    content_type = "text/plain"
    response_type = GetStatusAllResponse

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        return {"action": "statusall"}


def _parse_statusall_entries(payload: str) -> dict[str, dict[str, str]]:
    """Parse statusall response into device-id keyed dictionaries."""
    entries: dict[str, dict[str, str]] = {}

    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        parts = key.split(".")
        if len(parts) < 3:
            continue

        item_id = ".".join(parts[:2])
        field = ".".join(parts[2:])

        if not field:
            continue

        entries.setdefault(item_id, {})[field] = value

    return entries


def _device_type_from_id(item_id: str) -> str:
    """Infer device type from statusall id key."""
    if item_id.startswith("Sensor."):
        return TemperatureDeviceType.SENSOR
    if item_id.startswith("Heater."):
        return TemperatureDeviceType.HEATER
    if item_id.startswith("Fan."):
        return TemperatureDeviceType.FAN
    return TemperatureDeviceType.UNKNOWN


def _parse_status(
    status_raw: str | None,
) -> tuple[TemperatureDeviceStatus, int | None]:
    """Normalize status string and optional intensity value."""
    if not status_raw:
        return TemperatureDeviceStatus.UNKNOWN, None

    if status_raw.startswith("Running"):
        match = _RUNNING_INTENSITY_RE.fullmatch(status_raw)
        intensity = int(match.group(1)) if match else None
        return TemperatureDeviceStatus.RUNNING, intensity

    if status_raw == "Stopped":
        return TemperatureDeviceStatus.STOPPED, None

    if "Failure" in status_raw:
        return TemperatureDeviceStatus.FAILURE, None

    return TemperatureDeviceStatus.UNKNOWN, None


def _to_float(value: str | None) -> float | None:
    """Convert string to float when possible."""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _to_int(value: str | None) -> int | None:
    """Convert string to int when possible."""
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
