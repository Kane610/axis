"""Models for temperaturecontrol.cgi sensors, heaters, and fans.

The statusall response includes sensor readings and heater or fan status,
including actuator intensity and time until stop.
"""

from abc import abstractmethod
from dataclasses import dataclass
import enum
import re
from typing import Self

from .api import ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"

_RUNNING_INTENSITY_RE = re.compile(r"Running\[(\d+)%?\]")


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
class TemperatureDevice(ApiItem):
    """Base type for sensors and actuators parsed from statusall data."""

    @classmethod
    @abstractmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Build a temperature-device model from parsed statusall fields."""


@dataclass(frozen=True)
class TemperatureSensor(TemperatureDevice):
    """A temperature-reporting sensor (Sensor.Sx entries)."""

    celsius: float | None = None
    fahrenheit: float | None = None
    name: str | None = None

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Create sensor object from parsed statusall key-value fields."""
        return cls(
            id=data["id"],
            celsius=_to_float(data.get("Celsius")),
            fahrenheit=_to_float(data.get("Fahrenheit")),
            name=data.get("Name"),
        )


@dataclass(frozen=True)
class TemperatureActuator(TemperatureDevice):
    """Shared fields for heater and fan devices."""

    intensity: int | None = None
    status: TemperatureDeviceStatus = TemperatureDeviceStatus.UNKNOWN
    status_raw: str | None = None
    time_until_stop: int | None = None

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Create actuator object from parsed statusall key-value fields."""
        status_raw = data.get("Status")
        status, intensity = _parse_status(status_raw)
        return cls(
            id=data["id"],
            intensity=intensity,
            status=status,
            status_raw=status_raw,
            time_until_stop=_to_int(data.get("TimeUntilStop")),
        )


@dataclass(frozen=True)
class TemperatureHeater(TemperatureActuator):
    """A controllable heater (Heater.Hx entries)."""


@dataclass(frozen=True)
class TemperatureFan(TemperatureActuator):
    """A controllable fan (Fan.Fx entries)."""


_DEVICE_FACTORY: dict[str, type[TemperatureDevice]] = {
    "sensor": TemperatureSensor,
    "heater": TemperatureHeater,
    "fan": TemperatureFan,
}


@dataclass
class GetStatusAllResponse(ApiResponse[dict[str, TemperatureDevice]]):
    """Temperature sensor readings and heater or fan status, indexed by device ID."""

    data: dict[str, TemperatureDevice]

    @classmethod
    def decode(cls, bytes_data: bytes) -> GetStatusAllResponse:
        """Decode raw bytes into a typed response payload."""
        payload = bytes_data.decode("utf-8")
        parsed = _parse_statusall_entries(payload)
        data: dict[str, TemperatureDevice] = {}
        for group_key, factory in _DEVICE_FACTORY.items():
            for item_id, fields in parsed.get(group_key, {}).items():
                data[item_id] = factory.decode(fields)
        return cls(data=data)


@dataclass
class GetStatusAllRequest(ApiRequest[GetStatusAllResponse]):
    """Request sensor, heater, and fan status from temperaturecontrol.cgi."""

    method = "get"
    path = "/axis-cgi/temperaturecontrol.cgi"
    content_type = "text/plain"
    response_type = GetStatusAllResponse

    @property
    def params(self) -> dict[str, str]:
        """Select the temperature-control statusall action."""
        return {"action": "statusall"}


def _parse_statusall_entries(
    payload: str,
) -> dict[str, dict[str, dict[str, str]]]:
    """Group recognized sensor, heater, and fan fields by device entry ID."""
    sensors: dict[str, dict[str, str]] = {}
    heaters: dict[str, dict[str, str]] = {}
    fans: dict[str, dict[str, str]] = {}
    sensor_fields = {"Name", "Celsius", "Fahrenheit"}
    heater_fan_fields = {"Status", "TimeUntilStop"}

    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        parts = key.split(".")
        if len(parts) < 3:
            continue
        item_id = ".".join(parts[:2])
        field = ".".join(parts[2:])

        if item_id.startswith("Sensor."):
            if field not in sensor_fields:
                continue
            entry = sensors.setdefault(item_id, {"id": item_id})
            entry[field] = value
        elif item_id.startswith("Heater."):
            if field not in heater_fan_fields:
                continue
            entry = heaters.setdefault(item_id, {"id": item_id})
            entry[field] = value
        elif item_id.startswith("Fan."):
            if field not in heater_fan_fields:
                continue
            entry = fans.setdefault(item_id, {"id": item_id})
            entry[field] = value
        else:
            continue

    return {"sensor": sensors, "heater": heaters, "fan": fans}


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
