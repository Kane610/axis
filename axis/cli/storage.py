"""Compatibility imports for application records and local registry persistence."""

from axis.application.errors import StorageError
from axis.application.records import ConnectionSettings, DeviceRecord
from axis.application.storage import DeviceRegistry, default_config_path

__all__ = [
    "ConnectionSettings",
    "DeviceRecord",
    "DeviceRegistry",
    "StorageError",
    "default_config_path",
]
