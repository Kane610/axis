"""Test Axis user management.

pytest --cov-report term-missing --cov=axis.pwdgrp_cgi tests/test_pwdgrp_cgi.py
"""

from unittest.mock import AsyncMock

from axis.pwdgrp_cgi import SGRP_ADMIN, Users


def test_users():
    """Verify that you can list users."""
    mock_request = AsyncMock()
    users = Users(fixture, mock_request)

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


async def test_create():
    """Verify that you can create users."""
    mock_request = AsyncMock()
    users = Users(fixture, mock_request)

    await users.create("joe", pwd="abcd", sgrp=SGRP_ADMIN)
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={
            "action": "add",
            "user": "joe",
            "pwd": "abcd",
            "grp": "users",
            "sgrp": "viewer:operator:admin",
        },
    )

    await users.create("joe", pwd="abcd", sgrp=SGRP_ADMIN, comment="comment")
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={
            "action": "add",
            "user": "joe",
            "pwd": "abcd",
            "grp": "users",
            "sgrp": "viewer:operator:admin",
            "comment": "comment",
        },
    )


async def test_modify():
    """Verify that you can modify users."""
    mock_request = AsyncMock()
    users = Users(fixture, mock_request)

    await users.modify("joe", pwd="abcd")
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={"action": "update", "user": "joe", "pwd": "abcd"},
    )

    await users.modify("joe", sgrp=SGRP_ADMIN)
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={"action": "update", "user": "joe", "sgrp": "viewer:operator:admin"},
    )

    await users.modify("joe", comment="comment")
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={"action": "update", "user": "joe", "comment": "comment"},
    )

    await users.modify("joe", pwd="abcd", sgrp=SGRP_ADMIN, comment="comment")
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/pwdgrp.cgi",
        data={
            "action": "update",
            "user": "joe",
            "pwd": "abcd",
            "sgrp": "viewer:operator:admin",
            "comment": "comment",
        },
    )


async def test_delete():
    """Verify that you can delete users."""
    mock_request = AsyncMock()
    users = Users(fixture, mock_request)
    await users.delete("joe")

    mock_request.assert_called_with(
        "post", "/axis-cgi/pwdgrp.cgi", data={"action": "remove", "user": "joe"}
    )


def test_equals_in_value():
    """Verify that values containing `=` are parsed correctly."""
    mock_request = AsyncMock()
    fixture_with_equals = fixture + 'equals-in-value="xyz=="'
    Users(fixture_with_equals, mock_request)


fixture = """admin="usera,wwwa,wwwaop,wwwaovp,wwwao,wwwap,wwwaov,root"
anonymous=""
api-discovery=""
audio="streamer,sdk,audiocontrol"
basic-device-info=""
gpio="environment,actionengined,led,mediaclipcgi,iod,scheduled,ptzadm,"
operator="usera,usero,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,root"
ptz="usera,wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"
users="userv,usero,usera"
viewer="usera,usero,sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,userv,wwwv"
digusers="root,operator,viewer"
"""
