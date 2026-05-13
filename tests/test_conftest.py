"""Contract tests for shared HTTP mocking fixtures in conftest.py."""

import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

import pytest

import axis.models
from axis.models.api import ApiRequest

from tests.conftest import (
    MOCK_API_REQUEST_DIRECT_CONTENT_TYPES,
    MOCK_API_REQUEST_EXPLICIT_RESPONSE_CONTENT_TYPES,
    MockApiRequestAssertions,
    MockApiResponseSpec,
)
from tests.http_route_mock import HttpRouteMock

if TYPE_CHECKING:
    from axis.device import AxisDevice


class _JsonApiRequest(ApiRequest):
    method = "POST"
    path = "/axis-cgi/mock/json.cgi"
    content_type = "application/json"


class _PlainTextApiRequest(ApiRequest):
    method = "GET"
    path = "/axis-cgi/mock/plain.cgi"
    content_type = "text/plain"


class _XmlApiRequest(ApiRequest):
    method = "POST"
    path = "/axis-cgi/mock/xml.cgi"
    content_type = "text/xml"


class _UnsupportedTypeApiRequest(ApiRequest):
    method = "POST"
    path = "/axis-cgi/mock/unsupported-type.cgi"
    content_type = "application/octet-stream"


class _UnsupportedMethodApiRequest(ApiRequest):
    method = "DELETE"
    path = "/axis-cgi/mock/unsupported-method.cgi"
    content_type = "application/json"


class _LowerCaseMethodApiRequest(ApiRequest):
    method = "post"
    path = "/axis-cgi/mock/lowercase-method.cgi"
    content_type = "application/json"


class _BlankMethodApiRequest(ApiRequest):
    method = "   "
    path = "/axis-cgi/mock/blank-method.cgi"
    content_type = "application/json"


class _AssertionApiRequest(ApiRequest):
    method = "POST"
    path = "/axis-cgi/mock/assertions.cgi"
    content_type = "application/json"


class _ExplicitResponseOnlyApiRequest(ApiRequest):
    method = "POST"
    path = "/axis-cgi/mock/explicit-only.cgi"
    content_type = "application/octet-stream"


def _iter_api_request_classes() -> list[type[ApiRequest]]:
    request_classes: list[type[ApiRequest]] = []
    seen: set[type[ApiRequest]] = set()

    for module_info in pkgutil.walk_packages(
        axis.models.__path__,
        prefix=f"{axis.models.__name__}.",
    ):
        module = importlib.import_module(module_info.name)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(candidate, ApiRequest)
                and candidate is not ApiRequest
                and candidate.__module__ == module.__name__
                and candidate not in seen
            ):
                seen.add(candidate)
                request_classes.append(candidate)

    return request_classes


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


class TestMockApiRequestFixture:
    """Validate the request-class-driven route registration fixture contract."""

    async def test_registers_json_response(self, mock_api_request, http_route_mock):
        """JSON request content type maps to route.respond(json=...)."""
        expected = {"ok": True}
        route = mock_api_request(_JsonApiRequest, expected)

        assert route._json == expected
        assert route._text is None
        assert http_route_mock.resolve("POST", _JsonApiRequest.path) is route

    async def test_registers_plain_text_response(
        self, mock_api_request, http_route_mock
    ):
        """Plain-text request content type maps to route.respond(text=...)."""
        expected = "ok"
        route = mock_api_request(_PlainTextApiRequest, expected)

        assert route._text == expected
        assert route._json is None
        assert http_route_mock.resolve("GET", _PlainTextApiRequest.path) is route

    async def test_registers_xml_response_as_text(
        self, mock_api_request, http_route_mock
    ):
        """XML request content type maps to route.respond(text=...)."""
        expected = "<root><ok>true</ok></root>"
        route = mock_api_request(_XmlApiRequest, expected)

        assert route._text == expected
        assert route._json is None
        assert http_route_mock.resolve("POST", _XmlApiRequest.path) is route

    async def test_raises_for_unsupported_content_type(self, mock_api_request):
        """Unsupported content types raise a descriptive ValueError."""
        with pytest.raises(ValueError, match="Unsupported content type"):
            mock_api_request(_UnsupportedTypeApiRequest, "data")

    async def test_raises_for_unsupported_method(self, mock_api_request):
        """Unsupported methods raise a descriptive ValueError."""
        with pytest.raises(ValueError, match="Unsupported method"):
            mock_api_request(_UnsupportedMethodApiRequest, {"ok": True})

    async def test_accepts_lowercase_method_by_normalizing(self, mock_api_request):
        """Method normalization accepts lowercase request method declarations."""
        route = mock_api_request(_LowerCaseMethodApiRequest, {"ok": True})

        assert route.method == "POST"
        assert route.path == _LowerCaseMethodApiRequest.path

    async def test_raises_for_blank_method(self, mock_api_request):
        """Blank request methods raise a targeted validation error."""
        with pytest.raises(ValueError, match="non-empty string"):
            mock_api_request(_BlankMethodApiRequest, {"ok": True})

    async def test_accepts_explicit_json_response_spec(self, mock_api_request):
        """Explicit response spec can set JSON independent of request content type."""
        route = mock_api_request(
            _PlainTextApiRequest,
            response=MockApiResponseSpec(json={"ok": True}, status_code=201),
        )

        assert route._json == {"ok": True}
        assert route._text is None
        assert route._status_code == 201

    async def test_accepts_explicit_text_response_spec_with_headers(
        self, mock_api_request
    ):
        """Explicit response spec can set text, status code, and headers."""
        route = mock_api_request(
            _JsonApiRequest,
            response=MockApiResponseSpec(
                text="ok",
                status_code=202,
                headers={"X-Test": "true"},
            ),
        )

        assert route._json is None
        assert route._text == "ok"
        assert route._status_code == 202
        assert route._headers == {"X-Test": "true"}

    async def test_rejects_legacy_and_explicit_response_together(
        self, mock_api_request
    ):
        """Passing legacy response_data and response spec together is invalid."""
        with pytest.raises(ValueError, match="response_data or response"):
            mock_api_request(
                _JsonApiRequest,
                {"legacy": True},
                response=MockApiResponseSpec(json={"new": True}),
            )

    async def test_rejects_response_spec_with_multiple_payload_kinds(
        self, mock_api_request
    ):
        """Response spec must use a single payload kind."""
        with pytest.raises(ValueError, match="only one payload kind"):
            mock_api_request(
                _JsonApiRequest,
                response=MockApiResponseSpec(json={"a": 1}, text="b"),
            )

    async def test_explicit_response_spec_allows_unsupported_content_type(
        self, mock_api_request
    ):
        """Explicit response specs can mock request classes outside direct mapping."""
        route = mock_api_request(
            _ExplicitResponseOnlyApiRequest,
            response=MockApiResponseSpec(content=b"ok"),
        )

        assert route._content == b"ok"

    async def test_all_model_api_requests_are_mockable(self, mock_api_request):
        """Every ApiRequest class in axis.models remains mockable by the fixture."""
        failures: list[str] = []

        for request_class in _iter_api_request_classes():
            try:
                mock_api_request(
                    request_class,
                    response=MockApiResponseSpec(text="ok"),
                )
            except (AttributeError, TypeError, ValueError) as err:  # pragma: no cover
                failures.append(
                    f"{request_class.__module__}.{request_class.__name__}: {err}"
                )

        assert not failures

    def test_model_api_request_content_types_match_fixture_contract(self):
        """Current request-model content types stay inside the documented fixture contract."""
        request_content_types = {
            request_class.content_type for request_class in _iter_api_request_classes()
        }

        assert request_content_types <= (
            MOCK_API_REQUEST_DIRECT_CONTENT_TYPES
            | MOCK_API_REQUEST_EXPLICIT_RESPONSE_CONTENT_TYPES
        )

    async def test_assertion_hooks_allow_matching_request(
        self, mock_api_request, axis_device
    ):
        """Assertion hooks validate params, headers, and request body."""
        mock_api_request(
            _AssertionApiRequest,
            response=MockApiResponseSpec(text="ok"),
            assertions=MockApiRequestAssertions(
                content=b"payload",
                params={"camera": "1"},
                headers={"X-Test": "true"},
            ),
        )

        async with axis_device.config.session.post(
            f"{axis_device.config.url}{_AssertionApiRequest.path}",
            params={"camera": "1"},
            data=b"payload",
            headers={"X-Test": "true"},
        ) as response:
            assert response.status == 200
            assert await response.text() == "ok"

    async def test_assertion_hooks_fail_on_header_mismatch(
        self, mock_api_request, axis_device
    ):
        """Assertion mismatch returns 400 with a useful message."""
        mock_api_request(
            _AssertionApiRequest,
            response=MockApiResponseSpec(text="ok"),
            assertions=MockApiRequestAssertions(headers={"X-Test": "expected"}),
        )

        async with axis_device.config.session.post(
            f"{axis_device.config.url}{_AssertionApiRequest.path}",
            data=b"payload",
            headers={"X-Test": "other"},
        ) as response:
            assert response.status == 400
            assert "Expected header X-Test=expected" in await response.text()
