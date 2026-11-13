"""Test Axis restart API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from axis.errors import Unauthorized
from axis.models.restart_cgi import RestartRequest

from tests.conftest import MockApiResponseSpec

if TYPE_CHECKING:
    from axis.device import AxisDevice


async def test_restart(mock_api_request, axis_device: AxisDevice) -> None:
    """Verify that restart calls restart.cgi."""
    route = mock_api_request(RestartRequest, response=MockApiResponseSpec())

    await axis_device.vapix.restart_cgi.restart()

    assert route.called
    assert route.calls.last.request.method == "GET"
    assert route.calls.last.request.url.path == "/axis-cgi/restart.cgi"


async def test_restart_unauthorized(mock_api_request, axis_device: AxisDevice) -> None:
    """Verify that restart raises when the account is not an administrator."""
    mock_api_request(RestartRequest, response=MockApiResponseSpec(status_code=401))

    with pytest.raises(Unauthorized):
        await axis_device.vapix.restart_cgi.restart()
