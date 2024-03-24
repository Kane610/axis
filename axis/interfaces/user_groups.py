"""User group API.

Figure out what access rights an account has.
"""

from ..models.pwdgrp_cgi import User
from ..models.user_group import GetUserGroupRequest, GetUserGroupResponse
from .api_handler import ApiHandler


class UserGroups(ApiHandler[User]):
    """User group access rights for Axis devices."""

    async def _api_request(self) -> dict[str, User]:
        """Get API data method defined by subclass."""
        return await self.get_user_groups()

    async def get_user_groups(self) -> dict[str, User]:
        """Retrieve privilege rights for current user."""
        bytes_data = await self.vapix.api_request(GetUserGroupRequest())
        return GetUserGroupResponse.decode(bytes_data).data
