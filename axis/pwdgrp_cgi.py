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

from .api import APIItems

PROPERTY = 'Properties.API.HTTP.Version=3'

URL = '/axis-cgi/pwdgrp.cgi'
URL_GET = URL + '?action=get'

ADMIN = 'admin'
OPERATOR = 'operator'
VIEWER = 'viewer'
PTZ = 'ptz'

SGRP_VIEWER = VIEWER
SGRP_OPERATOR = '{}:{}'.format(VIEWER, OPERATOR)
SGRP_ADMIN = '{}:{}:{}'.format(VIEWER, OPERATOR, ADMIN)

REGEX_USER = re.compile(r'^[A-Z0-9]{1,14}$', re.IGNORECASE)
REGEX_PASS = re.compile(r'^[x20-x7e]{1,64}$')
REGEX_STRING = re.compile(r'[A-Z0-9]+', re.IGNORECASE)


class Users(APIItems):
    """Represents all users of a device."""

    def __init__(self, raw: str, request: str) -> None:
        super().__init__(raw, request, URL_GET, User)

    def create(self, user: str, *,
               pwd: str, sgrp: str, comment: str=None) -> None:
        """Create new user."""
        data = {
            'action': 'add',
            'user': user,
            'pwd': pwd,
            'grp': 'users',
            'sgrp': sgrp
        }

        if comment:
            data['comment'] = comment

        self._request('post', URL, data=data)

    def modify(self, user: str, *,
               pwd: str=None, sgrp: str=None, comment: str=None) -> None:
        """Update user."""
        data = {
            'action': 'update',
            'user': user
        }

        if pwd:
            data['pwd'] = pwd

        if sgrp:
            data['sgrp'] = sgrp

        if comment:
            data['comment'] = comment

        self._request('post', URL, data=data)

    def delete(self, user: str) -> None:
        """Remove user."""
        data = {
            'action': 'remove',
            'user': user
        }

        self._request('post', URL, data=data)

    def process_raw(self, raw: str) -> None:
        """Pre-process raw string.

        Prepare users to work with APIItems.
        Create booleans with user levels.
        """
        raw_dict = dict(group.split('=') for group in raw.splitlines())

        raw_users = {
            user: {
                group: user in REGEX_STRING.findall(raw_dict[group])
                for group in [ADMIN, OPERATOR, VIEWER, PTZ]
            }
            for user in REGEX_STRING.findall(raw_dict['users'])
        }

        super().process_raw(raw_users)


class User:
    """Represents a user."""

    def __init__(self, id: str, raw: dict, request: str) -> None:
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def name(self) -> str:
        return self.id

    @property
    def admin(self) -> bool:
        return self.raw[ADMIN]

    @property
    def operator(self) -> bool:
        return self.raw[OPERATOR]

    @property
    def viewer(self) -> bool:
        return self.raw[VIEWER]

    @property
    def ptz(self) -> bool:
        return self.raw[PTZ]
