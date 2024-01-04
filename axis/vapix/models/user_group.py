"""User group API.

Figure out what access rights an account has.
"""

from dataclasses import dataclass
from typing import Self

from .api import ApiRequest, ApiResponse
from .pwdgrp_cgi import User, UserGroupsT


@dataclass
class GetUserGroupRequest(ApiRequest):
    """Request object for listing users."""

    method = "get"
    path = "/axis-cgi/usergroup.cgi"
    content_type = "text/plain"


@dataclass
class GetUserGroupResponse(ApiResponse[dict[str, User]]):
    """Response object for listing ports."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: list[str] = bytes_data.decode().splitlines()

        if len(data) == 0:
            return cls(data={})

        group_list = []
        if len(data) == 2:
            group_list = data[1].split()

        user: UserGroupsT = {
            "user": data[0],
            "admin": "admin" in group_list,
            "operator": "operator" in group_list,
            "viewer": "viewer" in group_list,
            "ptz": "ptz" in group_list,
        }
        return cls(data={"0": User.decode(user)})
