"""Test Axis user groups API.

pytest --cov-report term-missing --cov=axis.user_groups tests/test_user_groups.py
"""

import pytest
import respx

from axis.vapix.interfaces.user_groups import UserGroups
from axis.vapix.models.pwdgrp_cgi import SecondaryGroup

from .conftest import HOST


@pytest.fixture
def user_groups(axis_device) -> UserGroups:
    """Return the user_groups mock object."""
    return UserGroups(axis_device.vapix)


@respx.mock
async def test_empty_response(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups._update()

    assert user_groups.get("0") is None


@respx.mock
async def test_root_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups._update()

    assert (user := user_groups.get("0"))
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz


@respx.mock
async def test_admin_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="administrator\nusers admin operator viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups._update()

    assert (user := user_groups.get("0"))
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


@respx.mock
async def test_operator_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="operator\nusers operator viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups._update()

    assert (user := user_groups.get("0"))
    assert user.privileges == SecondaryGroup.OPERATOR
    assert not user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


@respx.mock
async def test_viewer_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="viewer\nusers viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups._update()

    assert (user := user_groups.get("0"))
    assert user.privileges == SecondaryGroup.VIEWER
    assert not user.admin
    assert not user.operator
    assert user.viewer
    assert not user.ptz
