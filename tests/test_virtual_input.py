"""Test Axis virtual input API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from axis.errors import ResponseError
from axis.models.event_instance import ListEventInstancesRequest
from axis.models.parameters.param_cgi import ParamRequest
from axis.models.virtual_input import (
    ActivateVirtualInputRequest,
    DeactivateVirtualInputRequest,
    VirtualInputResponse,
)

from .event_fixtures import EVENT_INSTANCE_PIR_SENSOR, EVENT_INSTANCES

from tests.conftest import MockApiResponseSpec

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.virtual_input import VirtualInputHandler


def _response(body: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<VirtualInputResponse xmlns="http://www.axis.com/vapix/http_cgi/virtualinput1"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" SchemaVersion="1.0"'
        ' xsi:schemaLocation="http://www.axis.com/vapix/http_cgi/virtualinput1'
        ' http://www.axis.com/vapix/http_cgi/virtualinput1_0.xsd">'
        f"{body}</VirtualInputResponse>"
    ).encode()


def _success(action: str, state_changed: str) -> bytes:
    return _response(
        f"<Success><{action}Success><StateChanged>\n  {state_changed}\n  "
        f"</StateChanged></{action}Success></Success>"
    )


PORT_ERROR_RESPONSE = _response(
    "<Error><GeneralError><ErrorCode>20</ErrorCode>"
    "<ErrorDescription>Port must be an integer in the range [1..64]"
    "</ErrorDescription></GeneralError></Error>"
)

PROPERTIES_RESPONSE = """root.Properties.API.HTTP.Version=3
root.Properties.Firmware.BuildDate=Feb 15 2019 09:42
root.Properties.Firmware.BuildNumber=26
root.Properties.Firmware.Version=10.12.300
root.Properties.System.SerialNumber=ACCC12345678
"""


@pytest.fixture
def virtual_input(axis_device: AxisDevice) -> VirtualInputHandler:
    """Return the virtual input handler."""
    return axis_device.vapix.virtual_input


@pytest.mark.parametrize(
    ("properties", "supported"),
    [
        (PROPERTIES_RESPONSE + "root.Properties.VirtualInput.VirtualInput=yes\n", True),
        (PROPERTIES_RESPONSE, False),
    ],
)
async def test_supported(
    mock_api_request,
    virtual_input: VirtualInputHandler,
    properties: str,
    supported: bool,
) -> None:
    """Verify support is read from the VirtualInput property."""
    assert not virtual_input.supported

    mock_api_request(
        ParamRequest,
        response=MockApiResponseSpec(
            content=properties.encode(),
            headers={"Content-Type": "text/plain"},
        ),
    )
    await virtual_input.vapix.params.property_handler.update()

    assert virtual_input.supported is supported


def _mock_event_instances(mock_api_request, content: str):
    return mock_api_request(
        ListEventInstancesRequest,
        response=MockApiResponseSpec(
            content=content.encode(),
            headers={"Content-Type": "application/soap+xml; charset=utf-8"},
        ),
    )


async def test_update_lists_ports(
    mock_api_request, virtual_input: VirtualInputHandler
) -> None:
    """Verify ports are listed from the VirtualInput event instance."""
    route = _mock_event_instances(mock_api_request, EVENT_INSTANCES)

    await virtual_input.update()

    assert list(virtual_input) == [str(port) for port in range(1, 33)]
    assert virtual_input["1"].port == 1
    assert virtual_input["32"].active is None

    await virtual_input.update()
    assert route.call_count == 1


async def test_update_without_virtual_input_instance(
    mock_api_request, virtual_input: VirtualInputHandler
) -> None:
    """Verify no ports are listed if the device declares no virtual inputs."""
    _mock_event_instances(mock_api_request, EVENT_INSTANCE_PIR_SENSOR)

    await virtual_input.update()

    assert len(virtual_input) == 0


async def test_activate_and_deactivate_update_state(
    mock_api_request, virtual_input: VirtualInputHandler
) -> None:
    """Verify known port state is updated and subscribers are signalled."""
    _mock_event_instances(mock_api_request, EVENT_INSTANCES)
    await virtual_input.update()
    signalled: list[str] = []
    virtual_input.subscribe(signalled.append, "3")

    for request_cls, action, method, active in (
        (ActivateVirtualInputRequest, "Activate", "activate", True),
        (DeactivateVirtualInputRequest, "Deactivate", "deactivate", False),
    ):
        mock_api_request(
            request_cls,
            response=MockApiResponseSpec(
                content=_success(action, "true"),
                headers={"Content-Type": "text/xml"},
            ),
        )
        await getattr(virtual_input, method)(3)
        assert virtual_input["3"].active is active
        assert virtual_input["4"].active is None

    assert signalled == ["3", "3"]


@pytest.mark.parametrize(
    ("method", "request_cls", "action", "path"),
    [
        (
            "activate",
            ActivateVirtualInputRequest,
            "Activate",
            "/axis-cgi/virtualinput/activate.cgi",
        ),
        (
            "deactivate",
            DeactivateVirtualInputRequest,
            "Deactivate",
            "/axis-cgi/virtualinput/deactivate.cgi",
        ),
    ],
)
@pytest.mark.parametrize("state_changed", [True, False])
async def test_activate_and_deactivate(
    mock_api_request,
    virtual_input: VirtualInputHandler,
    method: str,
    request_cls: type[ActivateVirtualInputRequest | DeactivateVirtualInputRequest],
    action: str,
    path: str,
    state_changed: bool,
) -> None:
    """Verify activate and deactivate requests and their responses."""
    route = mock_api_request(
        request_cls,
        response=MockApiResponseSpec(
            content=_success(action, str(state_changed).lower()),
            headers={"Content-Type": "text/xml"},
        ),
    )

    assert await getattr(virtual_input, method)(10) is state_changed

    assert route.called
    assert route.calls.last.request.method == "GET"
    assert route.calls.last.request.url.path == path
    assert dict(route.calls.last.request.url.params) == {
        "schemaversion": "1",
        "port": "10",
    }


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (PORT_ERROR_RESPONSE, "Virtual input error 20"),
        (b"not xml", "Invalid virtual input response"),
        (b"<Other/>", "Invalid virtual input response"),
        (_response("<Success/>"), "Invalid virtual input response"),
        (_response("<Success><Other/></Success>"), "Invalid virtual input response"),
    ],
)
def test_response_errors(content: bytes, message: str) -> None:
    """Verify device errors and unexpected payloads raise ResponseError."""
    with pytest.raises(ResponseError, match=message):
        VirtualInputResponse.decode(content)
