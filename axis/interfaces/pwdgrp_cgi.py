"""Axis Vapix user management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036044

user: The user account name (1-14 characters), a non-existing user
    account name. Valid characters are a-z, A-Z and 0-9.
pwd: The unencrypted password (1-64 characters) for the account.
    ASCII characters from character code 32 to 126 are valid.
grp: An existing primary group name of the account.
    The recommended value for this argument is users.
sgrp: Colon separated existing secondary group names of the account.
    This argument sets the user access rights for the user account.
comment: The comment field of the account.
"""

from ..models.api_discovery import ApiId
from ..models.pwdgrp_cgi import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUsersRequest,
    GetUsersResponse,
    ModifyUserRequest,
    SecondaryGroup,
    User,
)
from .api_handler import ApiHandler


class Users(ApiHandler[User]):
    """Represents all users of a device."""

    api_id = ApiId.USER_MANAGEMENT

    @property
    def listed_in_parameters(self) -> bool:
        """Is pwdgrp.cgi supported."""
        if self.vapix.params.property_handler.supported and (
            self.vapix.params.property_handler["0"].api_http_version >= 3
        ):
            return True
        return False

    async def _api_request(self) -> dict[str, User]:
        """Get default data of basic device information."""
        return await self.list()

    async def list(self) -> dict[str, User]:
        """List current users."""
        data = await self.vapix.api_request(GetUsersRequest())
        return GetUsersResponse.decode(data).data

    async def create(
        self,
        user: str,
        *,
        pwd: str,
        sgrp: SecondaryGroup,
        comment: str | None = None,
    ) -> None:
        """Create new user."""
        await self.vapix.api_request(CreateUserRequest(user, pwd, sgrp, comment))

    async def modify(
        self,
        user: str,
        *,
        pwd: str | None = None,
        sgrp: SecondaryGroup | None = None,
        comment: str | None = None,
    ) -> None:
        """Update user."""
        await self.vapix.api_request(ModifyUserRequest(user, pwd, sgrp, comment))

    async def delete(self, user: str) -> None:
        """Remove user."""
        await self.vapix.api_request(DeleteUserRequest(user))
