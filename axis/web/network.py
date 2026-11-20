"""Enumerate local IPv4 interfaces for web device discovery."""

from dataclasses import dataclass
import socket

import psutil

from axis.application.errors import ErrorKind, OperationError


@dataclass(frozen=True)
class NetworkInterface:
    """An interface's stable system identifier and current IPv4 addresses."""

    name: str
    label: str
    addresses: tuple[str, ...]
    up: bool | None

    @property
    def available(self) -> bool:
        """Only scan interfaces known to be up with an IPv4 address."""
        return self.up is True and bool(self.addresses)


def network_interfaces() -> list[NetworkInterface]:
    """List interfaces and their current status and IPv4 addresses."""
    try:
        addresses = psutil.net_if_addrs()
        statuses = psutil.net_if_stats()
    except OSError as err:
        msg = "Cannot list local network interfaces."
        raise OperationError(msg, kind=ErrorKind.CONNECTION) from err
    return [
        NetworkInterface(
            name=name,
            label=name,
            addresses=tuple(
                address.address
                for address in addresses.get(name, [])
                if address.family == socket.AF_INET
            ),
            up=statuses[name].isup if name in statuses else None,
        )
        for name in sorted(addresses.keys() | statuses.keys())
    ]
