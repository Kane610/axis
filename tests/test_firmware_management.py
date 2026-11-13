"""Test Axis firmware management API."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from axis.errors import ResponseError, Unauthorized
from axis.models.api_discovery import Api
from axis.models.firmware_management import RebootRequest

from tests.conftest import MockApiResponseSpec

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.firmware_management import FirmwareManagementHandler


@pytest.fixture
def firmware_management(axis_device: AxisDevice) -> FirmwareManagementHandler:
    """Return the firmware management handler."""
    return axis_device.vapix.firmware_management


def test_supported(
    axis_device: AxisDevice, firmware_management: FirmwareManagementHandler
) -> None:
    """Verify support is read from API discovery."""
    assert not firmware_management.supported

    axis_device.vapix.api_discovery._items = {
        "fwmgr": Api.decode(
            {"id": "fwmgr", "version": "1.4", "name": "Firmware Management"}
        )
    }
    assert firmware_management.supported


async def test_reboot(
    mock_api_request, firmware_management: FirmwareManagementHandler
) -> None:
    """Verify that reboot calls the reboot method."""
    route = mock_api_request(
        RebootRequest,
        response=MockApiResponseSpec(
            json={
                "apiVersion": "1.0",
                "context": "Axis library",
                "method": "reboot",
                "data": {},
            }
        ),
    )

    await firmware_management.reboot()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/firmwaremanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "reboot",
    }


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (
            MockApiResponseSpec(
                json={
                    "apiVersion": "1.0",
                    "method": "reboot",
                    "error": {"code": 423, "message": "System is busy."},
                }
            ),
            "Firmware management error 423: System is busy.",
        ),
        (
            MockApiResponseSpec(content=b"not json"),
            "Invalid firmware management response",
        ),
        (
            MockApiResponseSpec(content=b"null"),
            "Invalid firmware management response",
        ),
        (
            MockApiResponseSpec(content=b"[]"),
            "Invalid firmware management response",
        ),
    ],
)
async def test_reboot_error(
    mock_api_request,
    firmware_management: FirmwareManagementHandler,
    response: MockApiResponseSpec,
    message: str,
) -> None:
    """Verify that device errors and malformed responses raise ResponseError."""
    mock_api_request(RebootRequest, response=response)

    with pytest.raises(ResponseError, match=message):
        await firmware_management.reboot()


async def test_reboot_unauthorized(
    mock_api_request, firmware_management: FirmwareManagementHandler
) -> None:
    """Verify that reboot raises when the account is not an administrator."""
    mock_api_request(RebootRequest, response=MockApiResponseSpec(status_code=401))

    with pytest.raises(Unauthorized):
        await firmware_management.reboot()
