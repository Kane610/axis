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

URL = '/axis-cgi/pwdgrp.cgi?action={action}'
USER = '&user={user}'
PWD = '&pwd={pwd}'
GRP = '&grp=users'
SGRP = '&sgrp={sgrp}'
COMMENT = '&comment={comment}'

SGRP_VIEWER = 'viewer'
SGRP_OPERATOR = 'viewer:operator'
SGRP_ADMIN = 'viewer:operator:admin'

REGEX_STRING = re.compile(r'[A-Z0-9]+', re.IGNORECASE)


class Users(APIItems):
    """Represents all users of a device."""

    def __init__(self, raw: str, request: str):
        super().__init__(raw, request, URL.format(action='get'), User)

    def create(self, user: str, pwd: str, sgrp: str, comment: str=None):
        """Create new user."""
        url = URL.format(action='add') + GRP
        url += USER.format(user=user)
        url += PWD.format(pwd=pwd)
        url += SGRP.format(sgrp=sgrp)
        if comment:
            url += COMMENT.format(comment=comment)
        self._request('get', url)

    def modify(self, user: str, pwd: str=None,
                    sgrp: str=None, comment: str=None):
        """Update user."""
        url = URL.format(action='update')
        url += USER.format(user=user)
        if pwd:
            url += PWD.format(pwd=pwd)
        if sgrp:
            url += SGRP.format(sgrp=sgrp)
        if comment:
            url += COMMENT.format(comment=comment)
        self._request('get', url)

    def delete(self, user: str):
        """Remove user."""
        url = URL.format(action='remove')
        url += USER.format(user=user)
        self._request('get', url)

    def process_raw(self, raw):
        """Pre-process raw string.

        Prepare users to work with APIItems.
        """
        raw_users = {}
        for user in REGEX_STRING.findall(raw['users']):
            for group in ['admin', 'operator', 'viewer']:
                if user in REGEX_STRING.findall(raw[group]):
                    raw_users[user] = group
                    break
        super().process_raw(raw_users)



class User:
    """Represents a user."""

    def __init__(self, id: str, raw: str, request: str):
        self.id = id
        self.raw = raw
        self._request = request
