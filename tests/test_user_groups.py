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
    await user_groups.update()

    assert user_groups.privileges == SecondaryGroup.UNKNOWN
    assert not user_groups.admin
    assert not user_groups.operator
    assert not user_groups.viewer
    assert not user_groups.ptz


@respx.mock
async def test_root_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == SecondaryGroup.ADMIN_PTZ

    assert user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert user_groups.ptz


@respx.mock
async def test_admin_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="administrator\nusers admin operator viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == SecondaryGroup.ADMIN
    assert user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert not user_groups.ptz


@respx.mock
async def test_operator_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="operator\nusers operator viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == SecondaryGroup.OPERATOR
    assert not user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert not user_groups.ptz


@respx.mock
async def test_viewer_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="viewer\nusers viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == SecondaryGroup.VIEWER
    assert not user_groups.admin
    assert not user_groups.operator
    assert user_groups.viewer
    assert not user_groups.ptz
