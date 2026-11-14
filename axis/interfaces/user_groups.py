"""User group API.

Figure out what access rights an account has.
"""

from ..models.pwdgrp_cgi import User
from ..models.user_group import GetUserGroupRequest
from .api_handler import ApiHandler


class UserGroups(ApiHandler[User]):
    """User group access rights for Axis devices."""

    async def _api_request(self) -> dict[str, User]:
        """Read the logged-in account's privileges for this handler's cached data."""
        return await self.get_user_groups()

    async def get_user_groups(self) -> dict[str, User]:
        """Retrieve privilege rights for current user."""
        response = await self.vapix.api_request(GetUserGroupRequest())
        return response.data
