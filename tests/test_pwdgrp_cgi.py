"""Test Axis user management.

pytest --cov-report term-missing --cov=axis.pwdgrp_cgi tests/test_pwdgrp_cgi.py
"""

import pytest
import urllib

import respx

from axis.pwdgrp_cgi import SGRP_ADMIN, Users

from .conftest import HOST


@pytest.fixture
def users(axis_device) -> Users:
    """Returns the api_discovery mock object."""
    return Users(fixture, axis_device.vapix.request)


def test_users(users):
    """Verify that you can list users."""
    assert users["userv"]
    assert users["userv"].name == "userv"
    assert users["userv"].viewer
    assert not users["userv"].operator
    assert not users["userv"].admin
    assert not users["userv"].ptz

    assert users["usero"]
    assert users["usero"].name == "usero"
    assert users["usero"].viewer
    assert users["usero"].operator
    assert not users["usero"].admin
    assert not users["usero"].ptz

    assert users["usera"]
    assert users["usera"].name == "usera"
    assert users["usera"].viewer
    assert users["usera"].operator
    assert users["usera"].admin
    assert users["usera"].ptz


def test_get_users_low_privileges(axis_device):
    users = Users("", axis_device.vapix.request)
    assert len(users) == 0


@respx.mock
@pytest.mark.asyncio
async def test_create(users):
    """Verify that you can create users."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi")

    await users.create("joe", pwd="abcd", sgrp=SGRP_ADMIN)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
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

    await users.create("joe", pwd="abcd", sgrp=SGRP_ADMIN, comment="comment")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
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


@respx.mock
@pytest.mark.asyncio
async def test_modify(users):
    """Verify that you can modify users."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi")

    await users.modify("joe", pwd="abcd")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "pwd": "abcd"}
        ).encode()
    )

    await users.modify("joe", sgrp=SGRP_ADMIN)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "sgrp": "viewer:operator:admin"}
        ).encode()
    )

    await users.modify("joe", comment="comment")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
        == urllib.parse.urlencode(
            {"action": "update", "user": "joe", "comment": "comment"}
        ).encode()
    )

    await users.modify("joe", pwd="abcd", sgrp=SGRP_ADMIN, comment="comment")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
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


@respx.mock
@pytest.mark.asyncio
async def test_delete(users):
    """Verify that you can delete users."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi")

    await users.delete("joe")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pwdgrp.cgi"
    assert (
        route.calls.last.request.content
        == urllib.parse.urlencode({"action": "remove", "user": "joe"}).encode()
    )


def test_equals_in_value(axis_device):
    """Verify that values containing `=` are parsed correctly."""
    assert Users(fixture + 'equals-in-value="xyz=="', axis_device.vapix.request)


fixture = """admin="usera,wwwa,wwwaop,wwwaovp,wwwao,wwwap,wwwaov,root"
anonymous=""
api-discovery=""
audio="streamer,sdk,audiocontrol"
basic-device-info=""
gpio="environment,actionengined,led,mediaclipcgi,iod,scheduled,ptzadm,"
operator="usera,usero,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,root"
ptz="usera,wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"
root="root"
users="userv,usero,usera"
viewer="usera,usero,sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,userv,wwwv"
digusers="root,operator,viewer"
"""
