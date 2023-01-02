"""Test Axis user groups API.

pytest --cov-report term-missing --cov=axis.user_groups tests/test_user_groups.py
"""

import pytest
import respx

from axis.vapix.interfaces.user_groups import URL, UserGroups

from .conftest import HOST


@pytest.fixture
def user_groups(axis_device) -> UserGroups:
    """Return the user_groups mock object."""
    return UserGroups(axis_device.vapix, "")


@respx.mock
@pytest.mark.asyncio
async def test_empty_response(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80{URL}").respond(
        text="",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == "unknown"
    assert not user_groups.admin
    assert not user_groups.operator
    assert not user_groups.viewer
    assert not user_groups.ptz


@respx.mock
@pytest.mark.asyncio
async def test_root_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80{URL}").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == "admin"

    assert user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert user_groups.ptz


@respx.mock
@pytest.mark.asyncio
async def test_admin_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80{URL}").respond(
        text="administrator\nusers admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == "admin"
    assert user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert user_groups.ptz


@respx.mock
@pytest.mark.asyncio
async def test_operator_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80{URL}").respond(
        text="operator\nusers operator viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == "operator"
    assert not user_groups.admin
    assert user_groups.operator
    assert user_groups.viewer
    assert not user_groups.ptz


@respx.mock
@pytest.mark.asyncio
async def test_viewer_user(user_groups):
    """Test get_supported_versions."""
    respx.get(f"http://{HOST}:80{URL}").respond(
        text="viewer\nusers viewer\n",
        headers={"Content-Type": "text/plain"},
    )
    await user_groups.update()

    assert user_groups.privileges == "viewer"
    assert not user_groups.admin
    assert not user_groups.operator
    assert user_groups.viewer
    assert not user_groups.ptz
