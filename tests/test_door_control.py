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
                "token": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
                "Name": "Test Door 1",
                "Description": "Test Door 1 Description",
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
                "token": "Axis-c2987ee0-28d5-4b53-8493-52977af927cf",
                "Name": "Test Door 2",
                "Description": "Test Door 2 Description",
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

    item = door_control["Axis-5fba94a4-8601-4627-bdda-cc408f69e026"]
    assert item.id == "Axis-5fba94a4-8601-4627-bdda-cc408f69e026"
    assert item.door_token == "Axis-5fba94a4-8601-4627-bdda-cc408f69e026"
    assert item.door_name == "Test Door 1"
    assert item.door_description == "Test Door 1 Description"

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

    item2 = door_control["Axis-c2987ee0-28d5-4b53-8493-52977af927cf"]
    assert item2.id == "Axis-c2987ee0-28d5-4b53-8493-52977af927cf"
    assert item2.door_token == "Axis-c2987ee0-28d5-4b53-8493-52977af927cf"
    assert item2.door_name == "Test Door 2"
    assert item2.door_description == "Test Door 2 Description"
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
                    "token": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
                    "Name": "Test Door 1",
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
                    "token": "Axis-c2987ee0-28d5-4b53-8493-52977af927cf",
                    "Name": "Test Door 2",
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
            "token": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
            "Name": "Test Door 1",
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
            "token": "Axis-c2987ee0-28d5-4b53-8493-52977af927cf",
            "Name": "Test Door 2",
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
                    "token": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
                    "Name": "Test Door 1",
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

    tokens = ["Axis-5fba94a4-8601-4627-bdda-cc408f69e026"]

    response = await door_control.get_door_info(tokens)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {
        "tdc:GetDoorInfo": {"Token": tokens}
    }

    assert response["DoorInfo"] == [
        {
            "token": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
            "Name": "Test Door 1",
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

    token = "Axis-5fba94a4-8601-4627-bdda-cc408f69e026"

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


@pytest.mark.parametrize(
    "input,expected", [
        ({"api_function": "tdc:AccessDoor", "method_name": "access_door"}, None),
        ({"api_function": "tdc:LockDoor", "method_name": "lock_door"}, None),
        ({"api_function": "tdc:UnlockDoor", "method_name": "unlock_door"}, None),
        ({"api_function": "tdc:BlockDoor", "method_name": "block_door"}, None),
        ({"api_function": "tdc:LockDownDoor", "method_name": "lock_down_door"}, None),
        ({"api_function": "tdc:LockDownReleaseDoor", "method_name": "lock_down_release_door"}, None),
        ({"api_function": "tdc:LockOpenDoor", "method_name": "lock_open_door"}, None),
        ({"api_function": "tdc:LockOpenReleaseDoor", "method_name": "lock_open_release_door"}, None),
        ({"api_function": "tdc:DoubleLockDoor", "method_name": "double_lock_door"}, None),
        ({"api_function": "axtdc:ReleaseDoor", "method_name": "release_door"}, None),
    ]
)
@respx.mock
async def test_door_requests(door_control, input: dict, expected: str):
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={}
    )

    token = "Axis-5fba94a4-8601-4627-bdda-cc408f69e026"

    response = await getattr(door_control, input["method_name"])(token)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {input["api_function"]: {"Token": token}}

    assert response == expected
