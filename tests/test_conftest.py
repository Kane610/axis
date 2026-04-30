"""Contract tests for shared HTTP mocking fixtures in conftest.py."""

from typing import TYPE_CHECKING

import pytest

from tests.http_route_mock import HttpRouteMock

if TYPE_CHECKING:
    from axis.device import AxisDevice


class TestHttpRouteMock:
    """Validate the single-device http_route_mock fixture contract."""

    async def test_returns_http_route_mock_instance(self, http_route_mock):
        """http_route_mock returns an HttpRouteMock."""
        assert isinstance(http_route_mock, HttpRouteMock)

    async def test_device_port_is_bound(self, http_route_mock, axis_device: AxisDevice):
        """http_route_mock binds the mock server port to axis_device."""
        assert axis_device.config.port != 0

    async def test_post_route_can_be_registered(self, http_route_mock):
        """Routes registered via .post() are resolvable."""
        http_route_mock.post("/axis-cgi/test.cgi").respond(json={"result": "ok"})
        route = http_route_mock.resolve("POST", "/axis-cgi/test.cgi")
        assert route is not None

    async def test_get_route_can_be_registered(self, http_route_mock):
        """Routes registered via .get() are resolvable."""
        http_route_mock.get("/axis-cgi/test.cgi").respond(text="ok")
        route = http_route_mock.resolve("GET", "/axis-cgi/test.cgi")
        assert route is not None

    async def test_calls_list_starts_empty(self, http_route_mock):
        """Global calls list is empty before any requests are made."""
        assert len(http_route_mock.calls) == 0

    async def test_route_call_count_starts_at_zero(self, http_route_mock):
        """Registered route starts with call_count == 0."""
        route = http_route_mock.post("/axis-cgi/test.cgi").respond(json={})
        assert route.call_count == 0

    async def test_unknown_path_resolves_to_none(self, http_route_mock):
        """Resolving an unregistered path returns None."""
        assert http_route_mock.resolve("POST", "/does/not/exist") is None


class TestHttpRouteMockFactory:
    """Validate the multi-device http_route_mock_factory fixture contract."""

    async def test_single_device_binding(
        self, http_route_mock_factory, axis_device: AxisDevice
    ):
        """Factory with one device binds that device's port."""
        mock = await http_route_mock_factory(axis_device)
        assert isinstance(mock, HttpRouteMock)
        assert axis_device.config.port != 0

    async def test_multi_device_binding_shares_server(
        self,
        http_route_mock_factory,
        axis_device: AxisDevice,
        axis_companion_device: AxisDevice,
    ):
        """Factory with two devices binds both to the same mock server port."""
        mock = await http_route_mock_factory(axis_device, axis_companion_device)
        assert isinstance(mock, HttpRouteMock)
        assert axis_device.config.port != 0
        assert axis_companion_device.config.port != 0
        assert axis_device.config.port == axis_companion_device.config.port

    async def test_factory_returns_independent_mocks(
        self,
        http_route_mock_factory,
        axis_device: AxisDevice,
        axis_companion_device: AxisDevice,
    ):
        """Each factory call returns a fresh HttpRouteMock with empty route registry."""
        mock_a = await http_route_mock_factory(axis_device)
        mock_b = await http_route_mock_factory(axis_companion_device)
        mock_a.post("/axis-cgi/a.cgi").respond(json={})
        assert mock_b.resolve("POST", "/axis-cgi/a.cgi") is None

    async def test_route_mock_api_surface(
        self, http_route_mock_factory, axis_device: AxisDevice
    ):
        """HttpRouteMock exposes the expected public API surface."""
        mock = await http_route_mock_factory(axis_device)
        assert hasattr(mock, "post")
        assert hasattr(mock, "get")
        assert hasattr(mock, "resolve")
        assert hasattr(mock, "calls")


@pytest.mark.parametrize(
    ("respond_kwargs", "expected_attr"),
    [
        ({"json": {"key": "value"}}, "_json"),
        ({"text": "plain text"}, "_text"),
        ({"content": b"bytes"}, "_content"),
    ],
)
async def test_route_respond_stores_payload(
    respond_kwargs, expected_attr, http_route_mock
):
    """Route.respond() stores the expected payload attribute."""
    route = http_route_mock.post("/axis-cgi/test.cgi")
    route.respond(**respond_kwargs)
    assert getattr(route, expected_attr) is not None


async def test_route_respond_status_code_shorthand(http_route_mock):
    """Route.respond(401) shorthand sets the status code."""
    route = http_route_mock.post("/axis-cgi/test.cgi")
    route.respond(401)
    assert route._status_code == 401


async def test_multi_route_responds_all(http_route_mock):
    """MultiRoute.respond() applies to all grouped paths."""
    multi = http_route_mock.post(
        "",
        path__in=("/axis-cgi/a.cgi", "/axis-cgi/b.cgi"),
    )
    multi.respond(json={"ok": True})
    for path in ("/axis-cgi/a.cgi", "/axis-cgi/b.cgi"):
        route = http_route_mock.resolve("POST", path)
        assert route is not None
        assert route._json == {"ok": True}


async def test_route_data_match_requires_expected_body(http_route_mock, axis_device):
    """Routes registered with data only match requests with the same body."""
    route = http_route_mock.post(
        "/axis-cgi/body.cgi", data={"key": "expected"}
    ).respond(text="ok")

    async with axis_device.config.session.post(
        f"{axis_device.config.url}/axis-cgi/body.cgi",
        data={"key": "other"},
    ) as response:
        assert response.status == 404

    assert not route.called
    assert route.call_count == 0


async def test_route_data_match_accepts_expected_body(http_route_mock, axis_device):
    """Routes registered with data match and capture calls for matching bodies."""
    route = http_route_mock.post(
        "/axis-cgi/body.cgi", data={"key": "expected"}
    ).respond(text="ok")

    async with axis_device.config.session.post(
        f"{axis_device.config.url}/axis-cgi/body.cgi",
        data={"key": "expected"},
    ) as response:
        assert response.status == 200
        assert await response.text() == "ok"

    assert route.called
    assert route.call_count == 1
