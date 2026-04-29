"""Test Axis user management."""

from typing import TYPE_CHECKING
import urllib

import pytest

from axis.models.pwdgrp_cgi import SecondaryGroup, User

if TYPE_CHECKING:
    from axis.interfaces.pwdgrp_cgi import Users


@pytest.fixture
def users(axis_device_aiohttp) -> Users:
    """Return the api_discovery mock object."""
    return axis_device_aiohttp.vapix.users


async def _setup_pwdgrp_route(
    aiohttp_mock_server,
    users: Users,
    *,
    text: str = "",
    content: bytes | None = None,
) -> list[dict[str, object]]:
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/pwdgrp.cgi",
        method="POST",
        response=content if content is not None else text,
        device=users,
        capture_body=True,
    )
    return requests


def test_user_class_privileges() -> None:
    """Test privilege case that shouldn't be able to arise."""
    bad_user = User.decode(
        {"user": "u", "admin": False, "operator": False, "viewer": False, "ptz": False}
    )

    assert bad_user
    assert bad_user.name == "u"
    assert not bad_user.viewer
    assert not bad_user.operator
    assert not bad_user.admin
    assert not bad_user.ptz
    assert bad_user.privileges == SecondaryGroup.UNKNOWN


async def test_users(aiohttp_mock_server, users):
    """Verify that you can list users."""
    await _setup_pwdgrp_route(aiohttp_mock_server, users, text=GET_USERS_RESPONSE)
    await users.update()

    assert users.initialized

    assert users["userv"]
    assert users["userv"].name == "userv"
    assert users["userv"].viewer
    assert not users["userv"].operator
    assert not users["userv"].admin
    assert not users["userv"].ptz
    assert users["userv"].privileges == SecondaryGroup.VIEWER

    assert users["uservp"]
    assert users["uservp"].name == "uservp"
    assert users["uservp"].viewer
    assert not users["uservp"].operator
    assert not users["uservp"].admin
    assert users["uservp"].ptz
    assert users["uservp"].privileges == SecondaryGroup.VIEWER_PTZ

    assert users["usero"]
    assert users["usero"].name == "usero"
    assert users["usero"].viewer
    assert users["usero"].operator
    assert not users["usero"].admin
    assert not users["usero"].ptz
    assert users["usero"].privileges == SecondaryGroup.OPERATOR

    assert users["userop"]
    assert users["userop"].name == "userop"
    assert users["userop"].viewer
    assert users["userop"].operator
    assert not users["userop"].admin
    assert users["userop"].ptz
    assert users["userop"].privileges == SecondaryGroup.OPERATOR_PTZ

    assert users["usera"]
    assert users["usera"].name == "usera"
    assert users["usera"].viewer
    assert users["usera"].operator
    assert users["usera"].admin
    assert users["usera"].ptz
    assert users["usera"].privileges == SecondaryGroup.ADMIN_PTZ


async def test_users_new_response(aiohttp_mock_server, users):
    """Verify that you can list users."""
    response = b'admin="root,axisconnect"\r\noperator="root,axisconnect"\r\nviewer="root,axisconnect"\r\nptz="root,axisconnect"\r\ndigusers="root,axisconnect"\r\n'
    await _setup_pwdgrp_route(aiohttp_mock_server, users, content=response)
    await users.update()

    assert users["root"]
    assert users["root"].name == "root"
    assert users["root"].viewer
    assert users["root"].operator
    assert users["root"].admin
    assert users["root"].ptz


async def test_create(aiohttp_mock_server, users):
    """Verify that you can create users."""
    requests = await _setup_pwdgrp_route(aiohttp_mock_server, users)

    await users.create("joe", pwd="abcd", sgrp=SecondaryGroup.ADMIN)

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {
                "action": "add",
                "user": "joe",
                "pwd": "abcd",
                "grp": "users",
                "sgrp": "viewer:operator:admin",
            }
        ).encode()
    )

    await users.create("joe", pwd="abcd", sgrp=SecondaryGroup.ADMIN, comment="comment")

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {
                "action": "add",
                "user": "joe",
                "pwd": "abcd",
                "grp": "users",
                "sgrp": "viewer:operator:admin",
                "comment": "comment",
            }
        ).encode()
    )


async def test_modify(aiohttp_mock_server, users):
    """Verify that you can modify users."""
    requests = await _setup_pwdgrp_route(aiohttp_mock_server, users)

    await users.modify("joe", pwd="abcd")

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "pwd": "abcd"}
        ).encode()
    )

    await users.modify("joe", sgrp=SecondaryGroup.ADMIN)

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "sgrp": "viewer:operator:admin"}
        ).encode()
    )

    await users.modify("joe", comment="comment")

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "comment": "comment"}
        ).encode()
    )

    await users.modify("joe", pwd="abcd", sgrp=SecondaryGroup.ADMIN, comment="comment")

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode(
            {
                "action": "update",
                "user": "joe",
                "pwd": "abcd",
                "sgrp": "viewer:operator:admin",
                "comment": "comment",
            }
        ).encode()
    )


async def test_delete(aiohttp_mock_server, users):
    """Verify that you can delete users."""
    requests = await _setup_pwdgrp_route(aiohttp_mock_server, users)

    await users.delete("joe")

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pwdgrp.cgi"
    assert (
        requests[-1]["body"]
        == urllib.parse.urlencode({"action": "remove", "user": "joe"}).encode()
    )


async def test_equals_in_value(aiohttp_mock_server, users):
    """Verify that values containing `=` are parsed correctly."""
    await _setup_pwdgrp_route(
        aiohttp_mock_server, users, text=GET_USERS_RESPONSE + 'equals-in-value="xyz=="'
    )
    await users.update()


async def test_no_equals_in_value(aiohttp_mock_server, users):
    """Verify that values containing `=` are parsed correctly."""
    await _setup_pwdgrp_route(aiohttp_mock_server, users, text="")
    await users.update()


GET_USERS_RESPONSE = """admin="usera,wwwa,wwwaop,wwwaovp,wwwao,wwwap,wwwaov,root"
anonymous=""
api-discovery=""
audio="streamer,sdk,audiocontrol"
basic-device-info=""
gpio="environment,actionengined,led,mediaclipcgi,iod,scheduled,ptzadm,"
operator="usera,usero,userop,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,root"
ptz="usera,userop,uservp,wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"
root="root"
users="userv,usero,userop,usera"
viewer="usera,usero,userop,uservp,sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,userv,wwwv"
digusers="root,operator,viewer"
"""
