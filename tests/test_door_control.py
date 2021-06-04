"""Test Axis Door Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import json
import pytest

import respx

from axis.door_control import DoorControl
from .conftest import HOST


@pytest.fixture
def door_control(axis_device) -> DoorControl:
    """Returns the door_control mock object."""
    return DoorControl(axis_device.vapix.request)


@respx.mock
async def test_update(door_control):
    """Test update method."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={"DoorInfo": [
            {
                "token": "Axis-accc8ea9abac:1550808050.595717000",
                "Name": "Main Door",
                "Description": "Main Door Description",
                "Capabilities": {
                    "Access": True,
                    "Lock": True,
                    "Unlock": True,
                    "Block": True,
                    "DoubleLock": True,
                    "LockDown": True,
                    "LockOpen": True,
                    "DoorMonitor": True,
                    "LockMonitor": False,
                    "DoubleLockMonitor": False,
                    "Alarm": True,
                    "Tamper": False,
                    "Warning": True,
                    "Configurable": True
                }
            },
            {
                "token": "Axis-accc8ee70fbe:1614733258.565014000",
                "Name": "North Gym Door",
                "Description": "North Gym Door Description",
                "Capabilities": {}
            }
        ]
        }
    )

    await door_control.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:GetDoorInfoList": {}}

    assert len(door_control.values()) == 2

    item = door_control["Axis-accc8ea9abac:1550808050.595717000"]
    assert item.id == "Axis-accc8ea9abac:1550808050.595717000"
    assert item.door_token == "Axis-accc8ea9abac:1550808050.595717000"
    assert item.door_name == "Main Door"
    assert item.door_description == "Main Door Description"

    # TODO: Check to see that comparing dict using "==" actually does what I want it to do
    assert item.door_capabilities == {
        "Access": True,
        "Lock": True,
        "Unlock": True,
        "Block": True,
        "DoubleLock": True,
        "LockDown": True,
        "LockOpen": True,
        "DoorMonitor": True,
        "LockMonitor": False,
        "DoubleLockMonitor": False,
        "Alarm": True,
        "Tamper": False,
        "Warning": True,
        "Configurable": True
    }

    item2 = door_control["Axis-accc8ee70fbe:1614733258.565014000"]
    assert item2.id == "Axis-accc8ee70fbe:1614733258.565014000"
    assert item2.door_token == "Axis-accc8ee70fbe:1614733258.565014000"
    assert item2.door_name == "North Gym Door"
    assert item2.door_description == "North Gym Door Description"
    # TODO: Check to see that comparing dict using "==" actually does what I want it to do
    assert item2.door_capabilities == {}


@respx.mock
async def test_get_service_capabilities(door_control):
    """Test get service capabilities API."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={
            "Capabilities": {
                "MaxLimit": 100,
                "GetDoorSupported": True,
                "SetDoorSupported": True,
                "PriorityConfigurationSupported": True
            }
        },
    )

    response = await door_control.get_service_capabilities()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:GetServiceCapabilities": {}}

    assert response["Capabilities"] == {
        "MaxLimit": 100,
        "GetDoorSupported": True,
        "SetDoorSupported": True,
        "PriorityConfigurationSupported": True
    }


@respx.mock
async def test_get_door_info_list(door_control):
    """Test get door list."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={
            "DoorInfo": [
                {
                    "token": "Axis-accc8ea9abac:1550808050.595717000",
                    "Name": "Main Door",
                    "Description": "",
                    "Capabilities": {
                        "Access": True,
                        "Lock": True,
                        "Unlock": True,
                        "Block": True,
                        "DoubleLock": True,
                        "LockDown": True,
                        "LockOpen": True,
                        "DoorMonitor": True,
                        "LockMonitor": False,
                        "DoubleLockMonitor": False,
                        "Alarm": True,
                        "Tamper": False,
                        "Warning": True,
                        "Configurable": True
                    }
                },
                {
                    "token": "Axis-accc8ee70fbe:1614733258.565014000",
                    "Name": "North Gym Door",
                    "Description": "",
                    "Capabilities": {}
                }
            ]
        }
    )

    response = await door_control.get_door_info_list()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:GetDoorInfoList": {}}

    assert response["DoorInfo"] == [
        {
            "token": "Axis-accc8ea9abac:1550808050.595717000",
            "Name": "Main Door",
            "Description": "",
            "Capabilities": {
                "Access": True,
                "Lock": True,
                "Unlock": True,
                "Block": True,
                "DoubleLock": True,
                "LockDown": True,
                "LockOpen": True,
                "DoorMonitor": True,
                "LockMonitor": False,
                "DoubleLockMonitor": False,
                "Alarm": True,
                "Tamper": False,
                "Warning": True,
                "Configurable": True
            }
        },
        {
            "token": "Axis-accc8ee70fbe:1614733258.565014000",
            "Name": "North Gym Door",
            "Description": "",
            "Capabilities": {}
        }
    ]


@respx.mock
async def test_get_door_info(door_control):
    """Test get door info from token(s)."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={
            "DoorInfo": [
                {
                    "token": "Axis-accc8ea9abac:1550808050.595717000",
                    "Name": "Main Door",
                    "Description": "",
                    "Capabilities": {
                        "Access": True,
                        "Lock": True,
                        "Unlock": True,
                        "Block": True,
                        "DoubleLock": True,
                        "LockDown": True,
                        "LockOpen": True,
                        "DoorMonitor": True,
                        "LockMonitor": False,
                        "DoubleLockMonitor": False,
                        "Alarm": True,
                        "Tamper": False,
                        "Warning": True,
                        "Configurable": True
                    }
                }
            ]
        }
    )

    tokens = ["Axis-accc8ea9abac:1550808050.595717000"]

    response = await door_control.get_door_info(tokens)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {
        "tdc:GetDoorInfo": {"Token": tokens}
    }

    assert response["DoorInfo"] == [
        {
            "token": "Axis-accc8ea9abac:1550808050.595717000",
            "Name": "Main Door",
            "Description": "",
            "Capabilities": {
                "Access": True,
                "Lock": True,
                "Unlock": True,
                "Block": True,
                "DoubleLock": True,
                "LockDown": True,
                "LockOpen": True,
                "DoorMonitor": True,
                "LockMonitor": False,
                "DoubleLockMonitor": False,
                "Alarm": True,
                "Tamper": False,
                "Warning": True,
                "Configurable": True
            }
        }
    ]


@respx.mock
async def test_get_door_state(door_control):
    """Test get door state(s)."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={
            "DoorState": {
                "DoorPhysicalState": "Closed",
                "Alarm": "Normal",
                "DoorMode": "Locked"
            }
        }
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.get_door_state(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {
        "tdc:GetDoorState": {"Token": token}
    }

    assert response["DoorState"] == {
        "DoorPhysicalState": "Closed",
        "Alarm": "Normal",
        "DoorMode": "Locked"
    }


@respx.mock
async def test_access_door(door_control):
    """Test access door """
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.access_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:AccessDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_lock_door(door_control):
    """Test lock door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.lock_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:LockDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_unlock_door(door_control):
    """Test unlock door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.unlock_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:UnlockDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_block_door(door_control):
    """Test block door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.block_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:BlockDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_lock_down_door(door_control):
    """Test lock down door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.lock_down_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:LockDownDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_lock_down_release_door(door_control):
    """Test lock down release door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.lock_down_release_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:LockDownReleaseDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_lock_open_door(door_control):
    """Test lock  open door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.lock_open_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:LockOpenDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_lock_open_release_door(door_control):
    """Test lock open release door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.lock_open_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:LockOpenReleaseDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_double_lock_door(door_control):
    """Test double lock door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.double_lock_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:DoubleLockDoor": {"Token": token}}

    assert response == {}


@respx.mock
async def test_release_door(door_control):
    """Test release door"""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-accc8ea9abac:1550808050.595717000"

    response = await door_control.release_door(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:ReleaseDoor": {"Token": token}}

    assert response == {}
