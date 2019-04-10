"""Test Axis user management.

pytest --cov-report term-missing --cov=axis.pwdgrp_cgi tests/test_pwdgrp_cgi.py
"""

import pytest
from unittest.mock import Mock

from axis.pwdgrp_cgi import SGRP_ADMIN, User, Users


def test_users():
    """Verify that you can list users."""
    mock_request = Mock()
    users = Users(fixture, mock_request)

    assert users['userv']
    assert users['userv'].name == 'userv'
    assert users['userv'].viewer
    assert not users['userv'].operator
    assert not users['userv'].admin
    assert not users['userv'].ptz

    assert users['usero']
    assert users['usero'].name == 'usero'
    assert users['usero'].viewer
    assert users['usero'].operator
    assert not users['usero'].admin
    assert not users['usero'].ptz

    assert users['usera']
    assert users['usera'].name == 'usera'
    assert users['usera'].viewer
    assert users['usera'].operator
    assert users['usera'].admin
    assert users['usera'].ptz


def test_create():
    """Verify that you can create users."""
    mock_request = Mock()
    users = Users(fixture, mock_request)

    users.create('joe', pwd='abcd', sgrp=SGRP_ADMIN)
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'add',
            'user': 'joe',
            'pwd': 'abcd',
            'grp': 'users',
            'sgrp': 'viewer:operator:admin'
    })

    users.create('joe', pwd='abcd', sgrp=SGRP_ADMIN, comment='comment')
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'add',
            'user': 'joe',
            'pwd': 'abcd',
            'grp': 'users',
            'sgrp': 'viewer:operator:admin',
            'comment': 'comment'
    })


def test_modify():
    """Verify that you can modify users."""
    mock_request = Mock()
    users = Users(fixture, mock_request)

    users.modify('joe', pwd='abcd')
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'update',
            'user': 'joe',
            'pwd': 'abcd'
    })

    users.modify('joe', sgrp=SGRP_ADMIN)
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'update',
            'user': 'joe',
            'sgrp': 'viewer:operator:admin'
    })

    users.modify('joe', comment='comment')
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'update',
            'user': 'joe',
            'comment': 'comment'
    })

    users.modify('joe', pwd='abcd', sgrp=SGRP_ADMIN, comment='comment')
    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'update',
            'user': 'joe',
            'pwd': 'abcd',
            'sgrp': 'viewer:operator:admin',
            'comment': 'comment'
    })


def test_delete():
    """Verify that you can delete users."""
    mock_request = Mock()
    users = Users(fixture, mock_request)
    users.delete('joe')

    mock_request.assert_called_with(
        'post', '/axis-cgi/pwdgrp.cgi',
        data={
            'action': 'remove',
            'user': 'joe'
    })


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
