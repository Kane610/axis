"""User group API.

Figure out what access rights an account has.
"""

from ..models.pwdgrp_cgi import ADMIN, OPERATOR, PTZ, VIEWER
from .api import APIItem, APIItems

URL = "/axis-cgi/usergroup.cgi"

UNKNOWN = "unknown"


class UserGroups(APIItems):
    """User group access rights for Axis devices."""

    def __init__(self, vapix: object) -> None:
        """Initialize user groups manager."""
        super().__init__(vapix, URL, APIItem)

    @staticmethod
    def pre_process_raw(raw: str) -> dict:  # type: ignore[override]
        """Process raw group list to generate a full list of what is and isnt supported."""
        raw_list = raw.splitlines()

        group_list = []
        if len(raw_list) == 2:
            group_list = raw_list[1].split()

        return {group: group in group_list for group in [ADMIN, OPERATOR, VIEWER, PTZ]}

    @property
    def privileges(self) -> str:
        """Return highest privileged role supported."""
        if self.admin:
            return ADMIN
        if self.operator:
            return OPERATOR
        if self.viewer:
            return VIEWER
        return UNKNOWN

    @property
    def admin(self) -> bool:
        """Is user admin."""
        if ADMIN in self:
            return self[ADMIN].raw  # type: ignore[return-value]
        return False

    @property
    def operator(self) -> bool:
        """Is user operator."""
        if OPERATOR in self:
            return self[OPERATOR].raw  # type: ignore[return-value]
        return False

    @property
    def viewer(self) -> bool:
        """Is user viewer."""
        if VIEWER in self:
            return self[VIEWER].raw  # type: ignore[return-value]
        return False

    @property
    def ptz(self) -> bool:
        """Is user ptz."""
        if PTZ in self:
            return self[PTZ].raw  # type: ignore[return-value]
        return False
