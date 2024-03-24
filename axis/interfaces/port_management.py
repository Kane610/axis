"""I/O Port Management API.

The I/O port management API makes it possible to retrieve
information about the ports and apply product dependent configurations
"""

from ..models.api_discovery import ApiId
from ..models.port_management import (
    API_VERSION,
    GetPortsRequest,
    GetPortsResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    Port,
    PortConfiguration,
    Sequence,
    SetPortsRequest,
    SetStateSequenceRequest,
)
from .api_handler import ApiHandler


class IoPortManagement(ApiHandler[Port]):
    """I/O port management for Axis devices."""

    api_id = ApiId.IO_PORT_MANAGEMENT
    default_api_version = API_VERSION

    async def _api_request(self) -> dict[str, Port]:
        """Get default data of I/O port management."""
        return await self.get_ports()

    async def get_ports(self) -> dict[str, Port]:
        """List ports."""
        bytes_data = await self.vapix.api_request(GetPortsRequest())
        return GetPortsResponse.decode(bytes_data).data

    async def set_ports(
        self, ports: list[PortConfiguration] | PortConfiguration
    ) -> None:
        """Configure one or more ports.

        Some of the available options are:
        * Setting a nice name that can be used in the user interface.
        * Configuring the states and what constitutes a normal
            and triggered state respectively.
            This will make triggers activate in either open or closed circuits.
        The reason the change is treated as a nice name is because it doesn’t
          affect the underlying behavior of the port.
        Devices with configurable ports can change the direction
          to either input or output.
        """
        await self.vapix.api_request(SetPortsRequest(ports))

    async def set_state_sequence(self, port_id: str, sequence: list[Sequence]) -> None:
        """Apply a sequence of state changes with a delay in milliseconds between states."""
        await self.vapix.api_request(SetStateSequenceRequest(port_id, sequence))

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        return GetSupportedVersionsResponse.decode(bytes_data).data

    async def open(self, port_id: str) -> None:
        """Shortcut method to open a port."""
        await self.set_ports(PortConfiguration(port_id, state="open"))

    async def close(self, port_id: str) -> None:
        """Shortcut method to close a port."""
        await self.set_ports(PortConfiguration(port_id, state="closed"))
