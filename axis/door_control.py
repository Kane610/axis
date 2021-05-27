"""Door Control API.

The Axis Door control API makes it possible to control the behavior and functionality
of physical access controls in the Axis devices (e.g. A1001, A1601)
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/vapix/doorcontrol"

API_DISCOVERY_ID = "door-control"
API_VERSION = "1.0"


class DoorControl(APIItems):
    """Door control for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, Door)

    # TODO: Question: Is this used to get status information for the door?  Or to update the object properties?
    async def update(self) -> None:
        raw = await self.get_door_info_list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of doors."""
        door_control_data = raw.get("DoorInfo", {})
        return {api["token"]: api for api in door_control_data}

    async def get_service_capabilities(self) -> dict:
        """List the capabilities of the door controller."""
        return await self._request(
            "post",
            URL,
            json={"tdc:GetServiceCapabilities": {}},
        )

    async def get_door_info_list(self) -> dict:
        """List the doors."""
        return await self._request(
            "post",
            URL,
            json={"tdc:GetDoorInfoList": {}},
        )

    async def get_door_info(self, door_tokens: list) -> dict:
        """List the door information."""
        return await self._request(
            "post",
            URL,
            json={"tdc:GetDoorInfo": {"Token": door_tokens}}
        )

    async def get_door_state(self, door_token: str) -> dict:
        """List the door information."""
        return await self._request(
            "post",
            URL,
            json={"tdc:GetDoorState": {"Token": door_token}}
        )

    # region Door Actions
    async def access_door(self, door_token: str) -> None:
        """Access the door. Use when a credential holder is granted access,
         for example by swiping a card in a card reader."""
        await self._request(
            "post",
            URL,
            json={"tdc:AccessDoor": {"Token": door_token}}
        )

    async def lock_door(self, door_token: str) -> None:
        """Lock the door."""
        await self._request(
            "post",
            URL,
            json={"tdc:LockDoor": {"Token": door_token}}
        )

    async def unlock_door(self, door_token: str) -> None:
        """Unlock the door until it is explicitly locked again."""
        await self._request(
            "post",
            URL,
            json={"tdc:UnlockDoor": {"Token": door_token}}
        )

    async def block_door(self, door_token: str) -> None:
        """Block the door."""
        await self._request(
            "post",
            URL,
            json={"tdc:BlockDoor": {"Token": door_token}}
        )

    async def lock_down_door(self, door_token: str) -> None:
        """Lock the door and prevent all other commands until a LockDownReleaseDoor command is sent."""
        await self._request(
            "post",
            URL,
            json={"tdc:LockDownDoor": {"Token": door_token}}
        )

    async def lock_down_release_door(self, door_token: str) -> None:
        """Release the door from the LockedDown state."""
        await self._request(
            "post",
            URL,
            json={"tdc:LockDownReleaseDoor": {"Token": door_token}}
        )

    async def lock_open_door(self, door_token: str) -> None:
        """Unlock the door and prevent all other commands until a LockOpenReleaseDoor command is sent."""
        await self._request(
            "post",
            URL,
            json={"tdc:LockOpenDoor": {"Token": door_token}}
        )

    async def lock_open_release_door(self, door_token: str) -> None:
        """Release the door from the LockedOpen state."""
        await self._request(
            "post",
            URL,
            json={"tdc:LockOpenReleaseDoor": {"Token": door_token}}
        )

    async def double_lock_door(self, door_token: str) -> None:
        """Lock the door with a double lock."""
        await self._request(
            "post",
            URL,
            json={"tdc:DoubleLockDoor": {"Token": door_token}}
        )

    async def release_door(self, door_token: str) -> None:
        """Release the door from a priority level."""
        await self._request(
            "post",
            URL,
            json={"axtdc:ReleaseDoor": {"Token": door_token}}
        )
    # endregion


class Door(APIItem):
    """API Discovery item."""

    @property
    def door_token(self) -> str:
        """Token of Door."""
        return self.raw["token"]

    @property
    def door_name(self) -> str:
        """Name of Door."""
        return self.raw["Name"]

    @property
    def door_description(self) -> str:
        """Description of Door."""
        return self.raw["Description"]

    @property
    def door_capabilities(self) -> dict:
        """Capabilities of Door."""
        return self.raw["Capabilities"]
