"""Axis Vapix parameter management."""

from dataclasses import dataclass
import enum
import logging
from typing import Any

from ..api import ApiRequest

LOGGER = logging.getLogger(__name__)


class ParameterGroup(enum.Enum):
    """Parameter groups."""

    AUDIO = "Audio"
    AUDIOSOURCE = "AudioSource"
    BANDWIDTH = "Bandwidth"
    BASICDEVICEINFO = "BasicDeviceInfo"
    BRAND = "Brand"
    HTTPS = "HTTPS"
    IMAGE = "Image"
    IMAGESOURCE = "ImageSource"
    INPUT = "Input"
    IOPORT = "IOPort"
    LAYOUT = "Layout"
    MEDIACLIP = "MediaClip"
    NETWORK = "Network"
    OUTPUT = "Output"
    PROPERTIES = "Properties"
    PTZ = "PTZ"
    RECORDING = "Recording"
    REMOTESERVICE = "RemoteService"
    SNMP = "SNMP"
    SOCKS = "SOCKS"
    STORAGE = "Storage"
    STREAMCACHE = "StreamCache"
    STREAMPROFILE = "StreamProfile"
    SYSTEM = "System"
    TAMPERING = "Tampering"
    TEMPERATURECONTROL = "TemperatureControl"
    TIME = "Time"
    WEBSERVICE = "WebService"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ParameterGroup":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unsupported parameter group %s", value)
        return ParameterGroup.UNKNOWN


def params_to_dict(params: str) -> dict[str, Any]:
    """Convert parameters from string to dictionary.

    From "root.IOPort.I1.Output.Active=closed"
    To {'root': {'IOPort': {'I1': {'Output': {'Active': 'closed'}}}}}
    """

    def convert(value: str) -> bool | int | str:
        """Convert value to Python type."""
        if value in ("true", "false", "yes", "no"):  # Boolean values
            return value in ("true", "yes")
        if value.lstrip("-").isnumeric():  # Positive/negative values
            return int(value)
        return value

    def populate(store: dict[str, Any], keys: str, v: bool | int | str) -> None:
        """Populate store with new keys and value.

        populate({}, "root.IOPort.I1.Output.Active", "closed")
        {'root': {'IOPort': {'I1': {'Output': {'Active': 'closed'}}}}}
        """
        k, _, keys = keys.partition(".")  # "root", ".", "IOPort.I1.Output.Active"
        populate(store.setdefault(k, {}), keys, v) if keys else store.update({k: v})

    param_dict: dict[str, Any] = {}
    for line in params.splitlines():
        keys, _, value = line.partition("=")
        populate(param_dict, keys, convert(value))
    return param_dict


@dataclass
class ParamRequest(ApiRequest):
    """Request object for listing parameters."""

    method = "get"
    path = "/axis-cgi/param.cgi"
    content_type = "text/plain"

    group: ParameterGroup | None = None

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        group = f"&group=root.{self.group.value}" if self.group else ""
        return {"action": f"list{group}"}
