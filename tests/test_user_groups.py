"""Test Axis user groups API.

pytest --cov-report term-missing --cov=axis.user_groups tests/test_user_groups.py
"""

from aiohttp import web
import pytest

from axis.interfaces.user_groups import UserGroups
from axis.models.pwdgrp_cgi import SecondaryGroup


@pytest.fixture
def user_groups(axis_device_aiohttp) -> UserGroups:
    """Return the user_groups mock object."""
    return UserGroups(axis_device_aiohttp.vapix)


async def test_empty_response(aiohttp_server, user_groups):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.Response(text="", headers={"Content-Type": "text/plain"})

    app = web.Application()
    app.router.add_get("/axis-cgi/usergroup.cgi", handle_request)
    server = await aiohttp_server(app)
    user_groups.vapix.device.config.port = server.port

    await user_groups.update()

    assert user_groups.get("0") is None


async def test_root_user(aiohttp_server, user_groups):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.Response(
            text="root\nroot admin operator ptz viewer\n",
            headers={"Content-Type": "text/plain"},
        )

    app = web.Application()
    app.router.add_get("/axis-cgi/usergroup.cgi", handle_request)
    server = await aiohttp_server(app)
    user_groups.vapix.device.config.port = server.port

    await user_groups.update()

    assert user_groups.initialized

    user = user_groups["0"]
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz


async def test_admin_user(aiohttp_server, user_groups):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.Response(
            text="administrator\nusers admin operator viewer\n",
            headers={"Content-Type": "text/plain"},
        )

    app = web.Application()
    app.router.add_get("/axis-cgi/usergroup.cgi", handle_request)
    server = await aiohttp_server(app)
    user_groups.vapix.device.config.port = server.port

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


async def test_operator_user(aiohttp_server, user_groups):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.Response(
            text="operator\nusers operator viewer\n",
            headers={"Content-Type": "text/plain"},
        )

    app = web.Application()
    app.router.add_get("/axis-cgi/usergroup.cgi", handle_request)
    server = await aiohttp_server(app)
    user_groups.vapix.device.config.port = server.port

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.OPERATOR
    assert not user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz


async def test_viewer_user(aiohttp_server, user_groups):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.Response(
            text="viewer\nusers viewer\n",
            headers={"Content-Type": "text/plain"},
        )

    app = web.Application()
    app.router.add_get("/axis-cgi/usergroup.cgi", handle_request)
    server = await aiohttp_server(app)
    user_groups.vapix.device.config.port = server.port

    await user_groups.update()

    user = user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.VIEWER
    assert not user.admin
    assert not user.operator
    assert user.viewer
    assert not user.ptz
