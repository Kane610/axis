"""User group API.

Figure out what access rights an account has.
"""

from ..models.pwdgrp_cgi import SecondaryGroup, User
from ..models.user_group import GetUserGroupRequest, GetUserGroupResponse
from .api_handler import ApiHandler


class UserGroups(ApiHandler[User]):
    """User group access rights for Axis devices."""

    async def _api_request(self) -> dict[str, User]:
        """Get API data method defined by subsclass."""
        return await self.get_user_groups()

    async def get_user_groups(self) -> dict[str, User]:
        """Retrieve privilege rights for current user."""
        bytes_data = await self.vapix.new_request(GetUserGroupRequest())
        return GetUserGroupResponse.decode(bytes_data).data

    @property
    def privileges(self) -> SecondaryGroup:
        """Return highest privileged role supported."""
        if (user := self.get("0")) is None:
            return SecondaryGroup.UNKNOWN
        return user.privileges

    @property
    def admin(self) -> bool:
        """Is user admin."""
        if (user := self.get("0")) is None:
            return False
        return user.admin

    @property
    def operator(self) -> bool:
        """Is user operator."""
        if (user := self.get("0")) is None:
            return False
        return user.operator

    @property
    def viewer(self) -> bool:
        """Is user viewer."""
        if (user := self.get("0")) is None:
            return False
        return user.viewer

    @property
    def ptz(self) -> bool:
        """Is user ptz."""
        if (user := self.get("0")) is None:
            return False
        return user.ptz
