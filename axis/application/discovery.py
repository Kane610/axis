"""Find Axis devices advertising their video service on the local IPv4 network.

Discovery runs only when requested. It does not log in, register devices, or
prompt the user.
"""

import asyncio
from contextlib import AsyncExitStack
from ipaddress import IPv4Address
import math
import re

from zeroconf import IPVersion, ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from .errors import ErrorKind, OperationError, _failure

DiscoveredDevice = dict[str, str]

AXIS_SERVICE_TYPE = "_axis-video._tcp.local."
AXIS_OUI = {"00:40:8c", "ac:cc:8e", "b8:a4:4f", "e8:27:25"}
_HEX_ONLY_RE = re.compile(r"[^0-9a-f]")
_AXIS_OUI_NORMALIZED = {prefix.replace(":", "") for prefix in AXIS_OUI}


def _normalize_macaddress(value: str) -> str:
    lowered = value.strip().lower().rstrip("*")
    return _HEX_ONLY_RE.sub("", lowered)


def is_axis_macaddress(macaddress: str) -> bool:
    """Recognize the Axis prefixes used by video-service discovery."""
    normalized = _normalize_macaddress(macaddress)
    if len(normalized) < 6:
        return False
    return normalized[:6] in _AXIS_OUI_NORMALIZED


def _extract_macaddress_property(properties: dict[bytes, bytes | None]) -> str | None:
    for raw_key, raw_value in properties.items():
        key = raw_key.decode("utf-8", errors="ignore").strip().lower()
        if key != "macaddress":
            continue
        if raw_value is None:
            continue
        value = raw_value.decode("utf-8", errors="ignore").strip()
        if value:
            return value
    return None


def _decode_discovery_properties(
    properties: dict[bytes, bytes | None],
) -> dict[str, str]:
    """Decode Zeroconf TXT properties to normalized string key/value pairs."""
    decoded: dict[str, str] = {}
    for raw_key, raw_value in properties.items():
        key = raw_key.decode("utf-8", errors="ignore").strip().lower()
        if not key or raw_value is None:
            continue
        value = raw_value.decode("utf-8", errors="ignore").strip()
        if value:
            decoded[key] = value
    return decoded


def _extract_discovery_metadata(
    properties: dict[bytes, bytes | None],
) -> dict[str, str]:
    """Extract user-facing metadata fields from Zeroconf TXT properties."""
    decoded = _decode_discovery_properties(properties)
    fields: dict[str, tuple[str, ...]] = {
        "module": ("module", "hw", "hardware", "hardwareid"),
        "model": ("model", "modelname", "prodshortname", "prodfullname"),
        "serial": ("serial", "serialnumber"),
        "firmware": ("firmware", "version", "firmwareversion"),
        "vendor": ("vendor", "manufacturer", "brand"),
    }
    metadata: dict[str, str] = {}
    for label, aliases in fields.items():
        for alias in aliases:
            value = decoded.get(alias)
            if value:
                metadata[label] = value
                break
    return metadata


def _zeroconf_instance_name(service_name: str) -> str:
    suffix = f".{AXIS_SERVICE_TYPE}"
    if service_name.endswith(suffix):
        return service_name[: -len(suffix)]
    return service_name


async def discover_axis_devices(scan_seconds: float = 5.0) -> list[DiscoveredDevice]:
    """Find Axis devices, preferring advertised non-link-local IPv4 addresses.

    Devices advertising only link-local addresses remain in the results, after
    devices with non-link-local addresses.
    """
    if not math.isfinite(scan_seconds) or scan_seconds < 0:
        msg = "Discovery duration must be finite and non-negative."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    discovered_names: set[str] = set()

    def _on_service_state_change(
        zeroconf: object,
        service_type: str,
        name: str,
        state_change: object,
    ) -> None:
        _ = (zeroconf, service_type)
        if state_change in {ServiceStateChange.Added, ServiceStateChange.Updated}:
            discovered_names.add(name)

    try:
        async with AsyncExitStack() as resources:
            azc = AsyncZeroconf(ip_version=IPVersion.V4Only)
            resources.push_async_callback(azc.async_close)
            browser = AsyncServiceBrowser(
                azc.zeroconf,
                [AXIS_SERVICE_TYPE],
                handlers=[_on_service_state_change],
            )
            resources.push_async_callback(browser.async_cancel)
            await asyncio.sleep(scan_seconds)

            entries: list[DiscoveredDevice] = []
            seen_hosts: set[str] = set()
            for service_name in sorted(discovered_names):
                info = AsyncServiceInfo(AXIS_SERVICE_TYPE, service_name)
                if not await info.async_request(azc.zeroconf, timeout=1500):
                    continue
                macaddress = _extract_macaddress_property(info.properties)
                if not macaddress or not is_axis_macaddress(macaddress):
                    continue
                addresses = info.parsed_addresses(IPVersion.V4Only)
                if not addresses:
                    continue
                host = min(
                    addresses, key=lambda address: IPv4Address(address).is_link_local
                )
                if host in seen_hosts:
                    continue
                seen_hosts.add(host)
                entries.append(
                    {
                        "host": host,
                        "name": _zeroconf_instance_name(service_name),
                        "macaddress": macaddress,
                        **_extract_discovery_metadata(info.properties),
                    }
                )
            return sorted(
                entries, key=lambda entry: IPv4Address(entry["host"]).is_link_local
            )
    except Exception as exc:  # noqa: BLE001 - safe boundary; cancellation propagates
        raise _failure(exc, message="Device discovery failed.") from None
