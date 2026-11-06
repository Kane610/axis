"""Virtual input API.

Activate and deactivate virtual input ports, which can be used as start event
or condition in the device's action rules. Virtual inputs are not listed in API
discovery, support is announced by Properties.VirtualInput.VirtualInput and the
available ports are listed in the VirtualInput event instance.

https://developer.axis.com/vapix/network-video/input-and-outputs/#virtual-input-api
"""

from dataclasses import replace

from ..models.event import EventTopic
from ..models.virtual_input import (
    ActivateVirtualInputRequest,
    DeactivateVirtualInputRequest,
    VirtualInput,
    VirtualInputObjectT,
)
from .api_handler import ApiHandler


class VirtualInputHandler(ApiHandler[VirtualInput]):
    """Virtual input ports of a device."""

    @property
    def listed_in_parameters(self) -> bool:
        """Is virtual input supported."""
        if prop := self.vapix.params.property_handler.get("0"):
            return prop.virtual_input
        return False

    async def _api_request(self) -> dict[str, VirtualInput]:
        """Get available ports from the VirtualInput event instance."""
        event_instances = self.vapix.event_instances
        if not event_instances.initialized:
            await event_instances.update()
        if (instance := event_instances.get(EventTopic.VIRTUAL_INPUT)) is None:
            return {}
        values = sorted(
            (value for item in instance.source.items for value in item.values),
            key=int,
        )
        ports: list[VirtualInputObjectT] = [{"port": value} for value in values]
        return VirtualInput.decode_to_dict(ports)

    async def activate(self, port: int) -> bool:
        """Activate virtual input port, return True if the state changed."""
        response = await self.vapix.api_request(ActivateVirtualInputRequest(port))
        self._set_state(port, active=True)
        return response.data

    async def deactivate(self, port: int) -> bool:
        """Deactivate virtual input port, return True if the state changed."""
        response = await self.vapix.api_request(DeactivateVirtualInputRequest(port))
        self._set_state(port, active=False)
        return response.data

    def _set_state(self, port: int, active: bool) -> None:
        """Store known port state and signal subscribers."""
        if (item := self.get(str(port))) is None:
            return
        self._items[item.id] = replace(item, active=active)
        self.signal_subscribers(item.id)
