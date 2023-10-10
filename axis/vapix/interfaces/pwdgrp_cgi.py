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

import re
from typing import Dict

from ..models.pwdgrp_cgi import (
    ADMIN,
    OPERATOR,
    PTZ,
    VIEWER,
    CreateUserRequest,
    DeleteUserRequest,
    GetUsersRequest,
    ModifyUserRequest,
    User,
)
from .api import APIItems
from .api_handler import ApiHandler

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/pwdgrp.cgi"
URL_GET = URL + "?action=get"

SGRP_VIEWER = VIEWER
SGRP_OPERATOR = "{}:{}".format(VIEWER, OPERATOR)
SGRP_ADMIN = "{}:{}:{}".format(VIEWER, OPERATOR, ADMIN)

REGEX_USER = re.compile(r"^[A-Z0-9]{1,14}$", re.IGNORECASE)
REGEX_PASS = re.compile(r"^[x20-x7e]{1,64}$")
REGEX_STRING = re.compile(r"[A-Z0-9]+", re.IGNORECASE)


class Users(APIItems):
    """Represents all users of a device."""

    item_cls = User
    path = URL_GET

    async def update(self) -> None:
        """Update list of current users."""
        users = await self.list()
        self.process_raw(users)

    @staticmethod
    def pre_process_raw(raw: str) -> dict:  # type: ignore[override]
        """Pre-process raw string.

        Prepare users to work with APIItems.
        Create booleans with user levels.
        """
        if "=" not in raw:
            return {}

        raw_dict: Dict[str, str] = dict(
            group.split("=", 1) for group in raw.splitlines()  # type: ignore
        )

        raw_users = ["root"] + REGEX_STRING.findall(raw_dict["users"])

        users = {
            user: {
                group: user in REGEX_STRING.findall(raw_dict[group])
                for group in [ADMIN, OPERATOR, VIEWER, PTZ]
            }
            for user in raw_users
        }

        return users

    async def list(self) -> str:
        """List current users."""
        data = await self.vapix.new_request(GetUsersRequest())
        return data.decode()

    async def create(
        self, user: str, *, pwd: str, sgrp: str, comment: str | None = None
    ) -> None:
        """Create new user."""
        await self.vapix.new_request(CreateUserRequest(user, pwd, sgrp, comment))

    async def modify(
        self,
        user: str,
        *,
        pwd: str | None = None,
        sgrp: str | None = None,
        comment: str | None = None,
    ) -> None:
        """Update user."""
        await self.vapix.new_request(ModifyUserRequest(user, pwd, sgrp, comment))

    async def delete(self, user: str) -> None:
        """Remove user."""
        await self.vapix.new_request(DeleteUserRequest(user))
