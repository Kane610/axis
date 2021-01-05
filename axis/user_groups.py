"""User group API.

Figure out what access rights an account has.
"""

from .api import APIItem, APIItems
from .pwdgrp_cgi import ADMIN, OPERATOR, PTZ, VIEWER

URL = "/axis-cgi/usergroup.cgi"

UNKNOWN = "unknown"


class UserGroups(APIItems):
    """User group access rights for Axis devices."""

    def __init__(self, raw: str, request: object) -> None:
        super().__init__(raw, request, URL, APIItem)

    @staticmethod
    def pre_process_raw(raw: str) -> dict:
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
        return self[ADMIN].raw

    @property
    def operator(self) -> bool:
        """Is user operator."""
        return self[OPERATOR].raw

    @property
    def viewer(self) -> bool:
        """Is user viewer."""
        return self[VIEWER].raw

    @property
    def ptz(self) -> bool:
        """Is user ptz."""
        return self[PTZ].raw
