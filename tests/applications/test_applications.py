"""Test parsing installed applications from the Axis applications API.

pytest --cov-report term-missing --cov=axis.applications.applications tests/applications/test_applications.py
"""

from io import BytesIO
from typing import TYPE_CHECKING

from aiohttp import web
import pytest

from axis.errors import ResponseError, Unauthorized
from axis.interfaces.vapix import UploadDigestError
from axis.models.applications.application import (
    ApplicationConfigResponse,
    ApplicationControlError,
    ApplicationInfoResponse,
    ApplicationLicense,
    ApplicationStatus,
    ControlApplicationRequest,
    ListApplicationsResponse,
)

from tests.conftest import MockApiRequestAssertions, MockApiResponseSpec

if TYPE_CHECKING:
    from axis.interfaces.applications import ApplicationsHandler


@pytest.fixture
def applications(axis_device) -> ApplicationsHandler:
    """Return the applications handler attached to the mocked device."""
    return axis_device.vapix.applications


@pytest.mark.parametrize("action", ["start", "stop", "restart", "remove"])
async def test_control_application(mock_api_request, applications, action):
    """Send documented POST query arguments and require an OK response."""
    route = mock_api_request(
        ControlApplicationRequest,
        response=MockApiResponseSpec(text="OK\n"),
        assertions=MockApiRequestAssertions(
            params={"action": action, "package": "Example & App"}
        ),
    )
    await applications.control_application(action, "Example & App")
    assert route.call_count == 1
    assert route.calls.last.request.method == "POST"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            b'<reply result="ok"><supportedSdks><sdk>acap3</sdk><sdk>acap4-native</sdk></supportedSdks></reply>',
            ["acap3", "acap4-native"],
        ),
        (
            b'<reply result="ok"><supportedSdks><sdk>acap3</sdk></supportedSdks></reply>',
            ["acap3"],
        ),
        (b'<reply result="ok"><supportedSdks/></reply>', []),
    ],
)
def test_supported_sdks(body, expected):
    """Parse multiple, singleton, and explicitly empty SDK lists."""
    assert ApplicationInfoResponse.decode(body).data == expected


@pytest.mark.parametrize(
    "body",
    [
        b"<other/>",
        b'<reply result="error"/>',
        b'<reply result="ok"/>',
        b'<reply result="ok"><supportedSdks><sdk><nested/></sdk></supportedSdks></reply>',
    ],
)
def test_invalid_sdk_response(body):
    """Do not present unsupported or malformed responses as an empty list."""
    with pytest.raises(ResponseError):
        ApplicationInfoResponse.decode(body)


@pytest.mark.parametrize(("value", "expected"), [("true", True), ("false", False)])
def test_policy_response(value, expected):
    """Parse only the device's actual boolean setting."""
    body = f'<reply result="ok"><param name="AllowUnsigned" value="{value}"/></reply>'
    assert ApplicationConfigResponse.decode(body.encode()).data is expected


@pytest.mark.parametrize(
    "body",
    [
        b'<reply result="error"/>',
        b'<reply result="ok"/>',
        b'<reply result="ok"><param name="AllowUnsigned" value="maybe"/></reply>',
    ],
)
def test_invalid_policy_response(body):
    """Reject missing, invalid, or rejected policies."""
    with pytest.raises(ResponseError):
        ApplicationConfigResponse.decode(body)


@pytest.mark.parametrize("signature", ["SignatureStatus", "SignedStatus"])
def test_application_optional_details(signature):
    """Handle both documented signature names and singleton/repeated elements."""
    body = f"""<reply result="ok"><application Name="app" {signature}="Signed" Bundled="Yes">
        <Resources><Resource name="camera" used="yes"/><Resource name="storage" used="no"/></Resources>
        <CompatibleOsVersions><VersionRange><Min>11</Min><Max>12</Max></VersionRange></CompatibleOsVersions>
        </application></reply>"""
    app = ListApplicationsResponse.decode(body.encode()).data["app"]
    assert app.status is ApplicationStatus.UNKNOWN
    assert app.license_status is ApplicationLicense.UNKNOWN
    assert app.signature_status == "Signed"
    assert app.bundled == "Yes"
    assert app.resources == (
        {"name": "camera", "used": "yes"},
        {"name": "storage", "used": "no"},
    )
    assert app.compatible_os_versions == ({"Min": "11", "Max": "12"},)


@pytest.mark.parametrize("element", ["Resources", "CompatibleOsVersions"])
def test_malformed_application_details(element):
    """Reject malformed nested application details."""
    with pytest.raises(ResponseError):
        ListApplicationsResponse.decode(
            f'<reply result="ok"><application Name="app"><{element}>bad</{element}></application></reply>'.encode()
        )


def test_invalid_nested_application_entry():
    """Reject malformed resource entries instead of treating them as metadata."""
    with pytest.raises(ResponseError):
        ListApplicationsResponse.decode(
            b'<reply result="ok"><application Name="app"><Resources>'
            b"<Resource>bad</Resource></Resources></application></reply>"
        )


async def test_sdk_handler(aiohttp_mock_server, applications):
    """Request supported SDKs from the application information endpoint."""
    await aiohttp_mock_server(
        "/axis-cgi/applications/info.cgi",
        response='<reply result="ok"><supportedSdks><sdk>acap3</sdk></supportedSdks></reply>',
        device=applications,
    )
    assert await applications.supported_sdks() == ["acap3"]


async def test_license_upload_form_and_removal(aiohttp_mock_server, applications):
    """Send modern license form data and remove with documented query parameters."""
    received = []

    async def handler(request):
        if request.query["action"] == "uploadlicensekey":
            part = await (await request.multipart()).next()
            received.append(
                (dict(request.query), part.name, part.filename, await part.read())
            )
        else:
            received.append(dict(request.query))
        return web.Response(text="OK")

    await aiohttp_mock_server(
        "/axis-cgi/applications/license.cgi", handler=handler, device=applications
    )
    with BytesIO(b"<license/>") as file:
        await applications.upload_license("example & app", file)
    await applications.remove_license("example & app")
    assert received == [
        (
            {"action": "uploadlicensekey", "package": "example & app"},
            "fileData",
            "license.xml",
            b"<license/>",
        ),
        {"action": "removelicensekey", "package": "example & app"},
    ]


async def test_application_policy_handlers(aiohttp_mock_server, applications):
    """Read and set policy with the documented parameters."""
    seen = []

    async def handler(request):
        seen.append(dict(request.query))
        return web.Response(
            text='<reply result="ok"><param name="AllowUnsigned" value="true"/></reply>'
        )

    await aiohttp_mock_server(
        "/axis-cgi/applications/config.cgi", handler=handler, device=applications
    )
    assert await applications.allow_unsigned()
    assert await applications.set_allow_unsigned(True)
    assert seen == [
        {"action": "get", "name": "AllowUnsigned"},
        {"action": "set", "name": "AllowUnsigned", "value": "true"},
    ]


@pytest.mark.parametrize(
    ("status", "error"), [(302, ResponseError), (401, Unauthorized)]
)
async def test_application_write_rejects_redirects_and_auth_without_replay(
    aiohttp_mock_server, applications, status, error
):
    """Never replay writes in response to redirects or Basic auth challenges."""
    applications.vapix.device.config.is_companion = True
    _, requests = await aiohttp_mock_server(
        "/axis-cgi/applications/control.cgi",
        response="",
        status=status,
        headers={
            "Location": "/axis-cgi/applications/control.cgi",
            "WWW-Authenticate": 'Basic realm="test"',
        },
        device=applications,
    )
    with pytest.raises(error):
        await applications.control_application("restart", "app")
    assert len(requests) == 1
    assert "Axis-Orig-Sw=true" in requests[0]["query"]


@pytest.mark.parametrize("response", [b"Error: 15", b"Error: 4", b"invalid"])
async def test_control_response_rejects_errors(
    mock_api_request, applications, response
):
    """HTTP 200 error or malformed bodies cannot look like success."""
    mock_api_request(
        ControlApplicationRequest, response=MockApiResponseSpec(content=response)
    )
    with pytest.raises(ResponseError) as raised:
        await applications.control_application("start", "example")
    if response.startswith(b"Error"):
        assert isinstance(raised.value, ApplicationControlError)


async def test_upload_multipart_streams_once(
    aiohttp_mock_server, applications: ApplicationsHandler, tmp_path
) -> None:
    """Send a bounded, seekable file as the documented multipart field."""
    received = []

    async def upload(request: web.Request) -> web.Response:
        field = await (await request.multipart()).next()
        assert field is not None
        received.append(
            (
                field.name,
                field.filename,
                field.headers.get("Content-Type"),
                await field.read(),
            )
        )
        assert request.content_length is not None
        return web.Response(text="OK")

    await aiohttp_mock_server(
        "/axis-cgi/applications/upload.cgi", handler=upload, device=applications
    )
    path = tmp_path / "package.eap"
    path.write_bytes(b"package bytes")
    with path.open("rb") as package:
        await applications.upload_application(package)
    assert received == [
        ("file", "application.eap", "application/octet-stream", b"package bytes")
    ]


@pytest.mark.parametrize("qop", ["auth,auth-int", "auth-int"])
async def test_digest_upload_never_buffers_auth_int(
    aiohttp_mock_server, applications: ApplicationsHandler, tmp_path, qop
) -> None:
    """Prefer streaming digest auth and reject auth-int-only challenges."""
    uploads = []

    async def preflight(request: web.Request) -> web.Response:
        if "Authorization" not in request.headers:
            return web.Response(
                status=401,
                headers={
                    "WWW-Authenticate": f'Digest realm="test", nonce="123", qop="{qop}"'
                },
            )
        return web.Response(text="OK")

    async def upload(request: web.Request) -> web.Response:
        uploads.append(request.headers["Authorization"])
        part = await (await request.multipart()).next()
        assert part is not None
        assert await part.read() == b"package"
        return web.Response(text="OK")

    await aiohttp_mock_server(
        {"/preflight": preflight, "/axis-cgi/applications/upload.cgi": upload},
        device=applications,
    )
    await applications.vapix.request("post", "/preflight")
    path = tmp_path / "package.eap"
    path.write_bytes(b"package")
    with path.open("rb") as package:
        if qop == "auth-int":
            with pytest.raises(UploadDigestError):
                await applications.upload_application(package)
            assert not uploads
        else:
            await applications.upload_application(package)
            assert len(uploads) == 1
            assert "qop=auth," in uploads[0]


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (200, "Error: 15", ApplicationControlError),
        (200, "bad", ResponseError),
        (302, "", ResponseError),
        (401, "", Unauthorized),
    ],
)
async def test_upload_rejects_bad_response_without_replay(
    aiohttp_mock_server,
    applications: ApplicationsHandler,
    tmp_path,
    status,
    body,
    error,
) -> None:
    """Malformed responses, device errors, and redirects are not success."""
    _, requests = await aiohttp_mock_server(
        "/axis-cgi/applications/upload.cgi",
        response=body,
        status=status,
        headers={"Location": "/axis-cgi/applications/upload.cgi"},
        device=applications,
    )
    path = tmp_path / "package.eap"
    path.write_bytes(b"package")
    with path.open("rb") as package, pytest.raises(error):
        await applications.upload_application(package)
    assert len(requests) == 1


@pytest.mark.parametrize("body", [b"<other/>", b'<reply result="error"/>'])
def test_invalid_application_list_is_not_empty_success(body: bytes) -> None:
    """Unexpected or rejected list responses are surfaced explicitly."""
    with pytest.raises(ResponseError):
        ListApplicationsResponse.decode(body)


def test_unknown_application_states_are_safe() -> None:
    """Unrecognized device states remain displayable without enabling start or stop."""
    assert ApplicationStatus("new-state") is ApplicationStatus.UNKNOWN
    assert ApplicationLicense("new-license") is ApplicationLicense.UNKNOWN


async def test_update_no_application(
    aiohttp_mock_server, applications: ApplicationsHandler
):
    """An empty application list initializes the handler without adding entries."""
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/applications/list.cgi",
        response=LIST_APPLICATION_EMPTY_RESPONSE,
        headers={"Content-Type": "text/xml"},
        device=applications,
    )

    await applications.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/applications/list.cgi"
    assert len(applications.values()) == 0


async def test_update_single_application(
    aiohttp_mock_server, applications: ApplicationsHandler
):
    """A single application response populates every exposed application field."""
    await aiohttp_mock_server(
        "/axis-cgi/applications/list.cgi",
        response=LIST_APPLICATION_RESPONSE,
        headers={"Content-Type": "text/xml"},
        device=applications,
        capture_requests=False,
    )

    await applications.update()

    assert applications.initialized
    assert len(applications.values()) == 1

    app = next(iter(applications.values()))
    assert app.application_id == "143440"
    assert app.configuration_page == "local/vmd/config.html"
    assert app.license_name == "Proprietary"
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "vmd"
    assert app.nice_name == "AXIS Video Motion Detection"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "4.4-5"


async def test_update_multiple_applications(
    aiohttp_mock_server, applications: ApplicationsHandler
):
    """A multi-application response preserves each application's metadata and status."""
    await aiohttp_mock_server(
        "/axis-cgi/applications/list.cgi",
        response=LIST_APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
        device=applications,
        capture_requests=False,
    )

    await applications.update()

    assert len(applications.values()) == 7

    apps = iter(applications.values())

    app = next(apps)
    assert app.application_id == "1234"
    assert app.configuration_page == "local/RemoteAccess/#"
    assert app.license_name == ""
    assert app.license_status == "Custom"
    assert app.license_expiration_date == ""
    assert app.name == "RemoteAccess"
    assert app.nice_name == "AXIS Remote Access solution"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "1.12"

    app = next(apps)
    assert app.application_id == "46396"
    assert app.configuration_page == "local/VMD3/setup.html"
    assert app.license_name == ""
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "VMD3"
    assert app.nice_name == "AXIS Video Motion Detection"
    assert app.status == "Stopped"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "3.2-1"

    app = next(apps)
    assert app.application_id == "1234"
    assert app.configuration_page == "local/drstn_notifier/about.inc"
    assert app.license_name == ""
    assert app.license_status == "Custom"
    assert app.license_expiration_date == ""
    assert app.name == "drstn_notifier"
    assert app.nice_name == "AXIS Door Station Notifier"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "1.0"

    app = next(apps)
    assert app.application_id == "143440"
    assert app.configuration_page == "local/vmd/config.html"
    assert app.license_name == ""
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "vmd"
    assert app.nice_name == "AXIS Video Motion Detection"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "4.2-0"

    app = next(apps)
    assert app.application_id == "47775"
    assert app.configuration_page == "local/fenceguard/config.html"
    assert app.license_name == "Proprietary"
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "fenceguard"
    assert app.nice_name == "AXIS Fence Guard"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "2.2-6"

    app = next(apps)
    assert app.application_id == "46775"
    assert app.configuration_page == "local/loiteringguard/config.html"
    assert app.license_name == "Proprietary"
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "loiteringguard"
    assert app.nice_name == "AXIS Loitering Guard"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "2.2-6"

    app = next(apps)
    assert app.application_id == "48170"
    assert app.configuration_page == "local/motionguard/config.html"
    assert app.license_name == "Proprietary"
    assert app.license_status == "None"
    assert app.license_expiration_date == ""
    assert app.name == "motionguard"
    assert app.nice_name == "AXIS Motion Guard"
    assert app.status == "Running"
    assert app.validation_result_page == ""
    assert app.vendor == "Axis Communications"
    assert app.vendor_page == "http://www.axis.com"
    assert app.version == "2.2-6"


async def test_responses_with_with_limitations(
    aiohttp_mock_server, applications: ApplicationsHandler
):
    """Application responses with optional fields can be parsed without errors."""
    await aiohttp_mock_server(
        "/axis-cgi/applications/list.cgi",
        response=Q1615_MKII_9_80_LIST_APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
        device=applications,
        capture_requests=False,
    )

    await applications.update()


LIST_APPLICATION_EMPTY_RESPONSE = """<reply result="ok">
</reply>"""

LIST_APPLICATION_RESPONSE = """<reply result="ok">
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.4-5" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
</reply>"""

LIST_APPLICATIONS_RESPONSE = """<reply result="ok">
 <application Name="RemoteAccess" NiceName="AXIS Remote Access solution" Vendor="Axis Communications" Version="1.12" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/RemoteAccess/#" VendorHomePage="http://www.axis.com" />
 <application Name="VMD3" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="3.2-1" ApplicationID="46396" License="None" Status="Stopped" ConfigurationPage="local/VMD3/setup.html" VendorHomePage="http://www.axis.com" />
 <application Name="drstn_notifier" NiceName="AXIS Door Station Notifier" Vendor="Axis Communications" Version="1.0" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/drstn_notifier/about.inc" VendorHomePage="http://www.axis.com" />
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.2-0" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" />
 <application Name="fenceguard" NiceName="AXIS Fence Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="47775" License="None" Status="Running" ConfigurationPage="local/fenceguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="loiteringguard" NiceName="AXIS Loitering Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="46775" License="None" Status="Running" ConfigurationPage="local/loiteringguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="motionguard" NiceName="AXIS Motion Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="48170" License="None" Status="Running" ConfigurationPage="local/motionguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
</reply>"""

Q1615_MKII_9_80_LIST_APPLICATIONS_RESPONSE = """<reply result="ok">
 <application Name="AxisConnectDeploymentAgentAcap" NiceName="AXIS Connect Deployment Agent" Vendor="Axis Communications" Version="1.3-438" ApplicationID="412994" License="None" Status="Running" LicenseName="AXIS" />
 <application Name="TrafficWiz" NiceName="AXIS Traffic Wizard" Vendor="Axis Communications" Version="1.4-3" License="None" Status="Stopped" ConfigurationPage="local/TrafficWiz/index.html" />
 <application Name="deviceDiagnostics" NiceName="AXIS Device Diagnostics" Vendor="Axis Communications" Version="4.228-0" ApplicationID="328106" License="None" Status="Running" ConfigurationPage="local/deviceDiagnostics/info.html" LicenseName="Proprietary" />
 <application Name="fenceguard" NiceName="AXIS Fence Guard" Vendor="Axis Communications" Version="2.2-4" ApplicationID="47775" License="None" Status="Running" ConfigurationPage="local/fenceguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="loiteringguard" NiceName="AXIS Loitering Guard" Vendor="Axis Communications" Version="2.2-4" ApplicationID="46775" License="None" Status="Stopped" ConfigurationPage="local/loiteringguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="motionguard" NiceName="AXIS Motion Guard" Vendor="Axis Communications" Version="2.2-4" ApplicationID="48170" License="None" Status="Running" ConfigurationPage="local/motionguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.5-2" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="webrtc" NiceName="AXIS WebRTC" Vendor="Axis Communications" Version="4.15-2" ApplicationID="413622" License="None" Status="Running" ConfigurationPage="local/webrtc/webrtc.html" LicenseName="Available" />
</reply>
"""
