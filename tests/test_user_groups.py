"""Test parsing account privilege membership from the user-group endpoint.

pytest --cov-report term-missing --cov=axis.user_groups tests/test_user_groups.py
"""

import pytest

from axis.interfaces.user_groups import UserGroups
from axis.models.pwdgrp_cgi import SecondaryGroup


@pytest.fixture
def user_groups(axis_device) -> UserGroups:
    """Return a user-group handler for the mocked device."""
    return UserGroups(axis_device.vapix)


async def test_empty_response(aiohttp_mock_server, user_groups):
    """An empty response leaves the handler without a user-group entry."""
    await aiohttp_mock_server(
        "/axis-cgi/usergroup.cgi",
        method="GET",
        response="",
        headers={"Content-Type": "text/plain"},
        device=user_groups,
        capture_requests=False,
    )

    await user_groups.update()

    assert user_groups.get("0") is None


async def test_root_user(aiohttp_mock_server, user_groups):
    """Parse root membership as administrator, operator, viewer, and PTZ access."""
    await aiohttp_mock_server(
        "/axis-cgi/usergroup.cgi",
        method="GET",
        response="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
        device=user_groups,
        capture_requests=False,
    )

    await user_groups.update()

    assert user_groups.initialized

    user = user_groups["0"]
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz


async def test_admin_user(aiohttp_mock_server, user_groups):
    """Parse administrator membership without granting PTZ access."""
    await aiohttp_mock_server(
        "/axis-cgi/usergroup.cgi",
        method="GET",
        response="administrator\nusers admin operator viewer\n",
        headers={"Content-Type": "text/plain"},
        device=user_groups,
        capture_requests=False,
    )

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


async def test_operator_user(aiohttp_mock_server, user_groups):
    """Parse operator membership without administrator or PTZ access."""
    await aiohttp_mock_server(
        "/axis-cgi/usergroup.cgi",
        method="GET",
        response="operator\nusers operator viewer\n",
        headers={"Content-Type": "text/plain"},
        device=user_groups,
        capture_requests=False,
    )

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.OPERATOR
    assert not user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


async def test_viewer_user(aiohttp_mock_server, user_groups):
    """Parse viewer-only membership without elevated privileges."""
    await aiohttp_mock_server(
        "/axis-cgi/usergroup.cgi",
        method="GET",
        response="viewer\nusers viewer\n",
        headers={"Content-Type": "text/plain"},
        device=user_groups,
        capture_requests=False,
    )

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.VIEWER
    assert not user.admin
    assert not user.operator
    assert user.viewer
    assert not user.ptz
