"""I/O Port Management API.

The I/O port management API makes it possible to retrieve
information about the ports and apply product dependent configurations
"""

from ..models.api_discovery import ApiId
from ..models.port_management import (
    API_VERSION,
    GetPortsRequest,
    GetSupportedVersionsRequest,
    Port,
    PortConfiguration,
    Sequence,
    SetPortsRequest,
    SetStateSequenceRequest,
)
from .api_handler import ApiHandler, HandlerGroup


class IoPortManagement(ApiHandler[Port]):
    """Read I/O port settings and change port configuration or output states."""

    api_id = ApiId.IO_PORT_MANAGEMENT
    default_api_version = API_VERSION
    handler_groups = (HandlerGroup.API_DISCOVERY,)

    async def _api_request(self) -> dict[str, Port]:
        """Read I/O port settings for this handler's cached data."""
        return await self.get_ports()

    async def get_ports(self) -> dict[str, Port]:
        """Read the device's I/O ports and their configuration."""
        response = await self.vapix.api_request(
            GetPortsRequest(api_version=self.api_version)
        )
        return response.data

    async def set_ports(
        self, ports: list[PortConfiguration] | PortConfiguration
    ) -> None:
        """Configure one or more ports.

        Options include display names, normal and triggered states, and,
        on supported devices, changing a port between input and output.
        Display-name changes do not alter the port's electrical behavior.
        """
        await self.vapix.api_request(
            SetPortsRequest(ports, api_version=self.api_version)
        )

    async def set_state_sequence(self, port_id: str, sequence: list[Sequence]) -> None:
        """Apply a sequence of state changes with a delay in milliseconds between states."""
        await self.vapix.api_request(
            SetStateSequenceRequest(
                port_id,
                sequence,
                api_version=self.api_version,
            )
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        response = await self.vapix.api_request(GetSupportedVersionsRequest())
        return response.data

    async def open(self, port_id: str) -> None:
        """Shortcut method to open a port."""
        await self.set_ports(PortConfiguration(port_id, state="open"))

    async def close(self, port_id: str) -> None:
        """Shortcut method to close a port."""
        await self.set_ports(PortConfiguration(port_id, state="closed"))
