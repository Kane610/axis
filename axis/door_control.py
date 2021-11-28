"""Door Control API.

The Axis Door control API makes it possible to control the behavior and functionality
of physical access controls in the Axis devices (e.g. A1001, A1601)
"""

from .api import APIItem, APIItems

URL = "/vapix/doorcontrol"

API_DISCOVERY_ID = "door-control"

CAPABILITY_ACCESS = "Access"
CAPABILITY_LOCK = "Lock"
CAPABILITY_UNLOCK = "Unlock"
CAPABILITY_BLOCK = "Block"
CAPABILITY_DOUBLE_LOCK = "DoubleLock"
CAPABILITY_LOCK_DOWN = "LockDown"
CAPABILITY_LOCK_OPEN = "LockOpen"
CAPABILITY_DOOR_MONITOR = "DoorMonitor"
CAPABILITY_LOCK_MONITOR = "LockMonitor"
CAPABILITY_DOUBLE_LOCK_MONITOR = "DoubleLockMonitor"
CAPABILITY_ALARM = "Alarm"
CAPABILITY_TAMPER = "Tamper"
CAPABILITY_WARNING = "Warning"
CAPABILITY_CONFIGURABLE = "Configurable"

SUPPORTED_CAPABILITIES = (
    CAPABILITY_ACCESS,
    CAPABILITY_LOCK,
    CAPABILITY_UNLOCK,
    CAPABILITY_BLOCK,
    CAPABILITY_DOUBLE_LOCK,
    CAPABILITY_LOCK_DOWN,
    CAPABILITY_LOCK_OPEN,
    CAPABILITY_DOOR_MONITOR,
    CAPABILITY_LOCK_MONITOR,
    CAPABILITY_DOUBLE_LOCK_MONITOR,
    CAPABILITY_ALARM,
    CAPABILITY_TAMPER,
    CAPABILITY_WARNING,
    CAPABILITY_CONFIGURABLE
)


class DoorControl(APIItems):
    """Door control for Axis devices."""

    def __init__(self, request: object) -> None:
        """Initialize door control manager."""
        super().__init__({}, request, URL, Door)

    # TODO: Question: Is this used to get status information for the door?  Or to update the object properties?
    async def update(self) -> None:
        """Refresh data."""
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
        """Access a Door.

        It invokes the functionality typically used when a card holder presents a card to a card reader at the door and is granted access.
        The DoorMode shall change to Accessed.
        The Door shall remain accessible for the defined time as configured in the device.
        When the time span elapses, the DoorMode shall change back to its previous state.
        A device must have the Lock capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:AccessDoor": {"Token": door_token}}
        )

    async def lock_door(self, door_token: str) -> None:
        """Lock a Door.

        The DoorMode shall change to Locked.
        A device must have the Lock capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:LockDoor": {"Token": door_token}}
        )

    async def unlock_door(self, door_token: str) -> None:
        """Unlock a Door until it is explicitly locked again.

        The DoorMode shall change to Unlocked.
        A device must have the Unlock capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:UnlockDoor": {"Token": door_token}}
        )

    async def block_door(self, door_token: str) -> None:
        """Block a Door and prevent momentary access (AccessDoor command).

        The DoorMode shall change to Blocked.
        A device must have the Block capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:BlockDoor": {"Token": door_token}}
        )

    async def lock_down_door(self, door_token: str) -> None:
        """Locks down a door and prevents other actions until a LockDownReleaseDoor command is invoked.

        The DoorMode shall change to LockedDown.
        The device shall ignore other door control commands until a LockDownReleaseDoor command is performed.
        A device must have the LockDown capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:LockDownDoor": {"Token": door_token}}
        )

    async def lock_down_release_door(self, door_token: str) -> None:
        """Releases the LockedDown state of a Door.

        The DoorMode shall change back to its previous/next state.
        It is not defined what the previous/next state shall be, but typically - Locked.
        This method will only succeed if the current DoorMode is LockedDown.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:LockDownReleaseDoor": {"Token": door_token}}
        )

    async def lock_open_door(self, door_token: str) -> None:
        """Unlocks a Door and prevents other actions until LockOpenReleaseDoor method is invoked.

        The DoorMode shall change to LockedOpen.
        The device shall ignore other door control commands until a LockOpenReleaseDoor command is performed.
        A device must have the LockOpen capability to utilize this method.
        """
        await self._request(
            "post",
            URL,
            json={"tdc:LockOpenDoor": {"Token": door_token}}
        )

    async def lock_open_release_door(self, door_token: str) -> None:
        """Releases the LockedOpen state of a Door.

        The DoorMode shall change state from the LockedOpen state back to its previous/next state.
        It is not defined what the previous/next state shall be, but typically - Unlocked.
        This method shall only succeed if the current DoorMode is LockedOpen.
        """
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
        """Door Description."""
        return self.raw["Description"]

    @property
    def door_capabilities(self) -> dict:
        """Capabilities of Door."""
        return self.raw["Capabilities"]

    async def is_capable_of(self, capability: str) -> bool:
        """Retrieve whether door has the specified capability."""
        if capability not in SUPPORTED_CAPABILITIES:
            return False
        return self.raw["Capabilities"][capability]
