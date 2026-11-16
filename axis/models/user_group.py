"""Models for looking up the current account's access groups through usergroup.cgi.

The response describes whether the account is an administrator, operator, viewer,
or PTZ user.
"""

from dataclasses import dataclass
from typing import Self

from .api import ApiRequest, ApiResponse
from .pwdgrp_cgi import User, UserGroupsT


@dataclass
class GetUserGroupResponse(ApiResponse[dict[str, User]]):
    """Current account and its access-group membership."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the account name and group list returned by usergroup.cgi."""
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


@dataclass
class GetUserGroupRequest(ApiRequest[GetUserGroupResponse]):
    """Request the access groups assigned to the current account."""

    method = "get"
    path = "/axis-cgi/usergroup.cgi"
    content_type = "text/plain"
    response_type = GetUserGroupResponse
