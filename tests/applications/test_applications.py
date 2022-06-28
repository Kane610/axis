"""Test Axis Applications API.

pytest --cov-report term-missing --cov=axis.applications.applications tests/applications/test_applications.py
"""

import pytest

import respx

from axis.vapix.interfaces.applications import Applications

from ..conftest import HOST


@pytest.fixture
def applications(axis_device) -> Applications:
    """Returns the applications mock object."""
    return Applications(axis_device.vapix.request)


@respx.mock
@pytest.mark.asyncio
async def test_update_no_application(applications):
    """Test update applicatios call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=list_application_empty_response,
        headers={"Content-Type": "text/xml"},
    )

    await applications.update()

    assert route.called
    assert len(applications.values()) == 0


@respx.mock
@pytest.mark.asyncio
async def test_update_single_application(applications):
    """Test update applications call."""
    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=list_application_response,
        headers={"Content-Type": "text/xml"},
    )
    await applications.update()

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


@respx.mock
@pytest.mark.asyncio
async def test_update_multiple_applications(applications):
    """Test update applicatios call."""
    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=list_applications_response,
        headers={"Content-Type": "text/xml"},
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


@respx.mock
@pytest.mark.asyncio
async def test_list_single_application(applications):
    """Test list applications call.

    Single application is sent as a dict, multiple applications are sent in a list.
    """
    list_route = respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=list_application_response,
        headers={"Content-Type": "text/xml"},
    )
    raw = await applications.list()

    assert list_route.calls.last.request.method == "POST"
    assert list_route.calls.last.request.url.path == "/axis-cgi/applications/list.cgi"

    assert "reply" in raw
    assert "application" in raw["reply"]
    assert raw["reply"]["application"]["@NiceName"] == "AXIS Video Motion Detection"


@respx.mock
@pytest.mark.asyncio
async def test_list_multiple_applications(applications):
    """Test list applications call.

    Single application is sent as a dict, multiple applications are sent in a list.
    """
    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=list_applications_response,
        headers={"Content-Type": "text/xml"},
    )
    raw = await applications.list()

    assert "reply" in raw
    assert "application" in raw["reply"]
    assert raw["reply"]["application"][0]["@NiceName"] == "AXIS Remote Access solution"
    assert raw["reply"]["application"][1]["@NiceName"] == "AXIS Video Motion Detection"
    assert raw["reply"]["application"][2]["@NiceName"] == "AXIS Door Station Notifier"
    assert raw["reply"]["application"][3]["@NiceName"] == "AXIS Video Motion Detection"
    assert raw["reply"]["application"][4]["@NiceName"] == "AXIS Fence Guard"
    assert raw["reply"]["application"][5]["@NiceName"] == "AXIS Loitering Guard"
    assert raw["reply"]["application"][6]["@NiceName"] == "AXIS Motion Guard"


list_application_empty_response = """<reply result="ok">
</reply>"""

list_application_response = """<reply result="ok">
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.4-5" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
</reply>"""

list_applications_response = """<reply result="ok">
 <application Name="RemoteAccess" NiceName="AXIS Remote Access solution" Vendor="Axis Communications" Version="1.12" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/RemoteAccess/#" VendorHomePage="http://www.axis.com" />
 <application Name="VMD3" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="3.2-1" ApplicationID="46396" License="None" Status="Stopped" ConfigurationPage="local/VMD3/setup.html" VendorHomePage="http://www.axis.com" />
 <application Name="drstn_notifier" NiceName="AXIS Door Station Notifier" Vendor="Axis Communications" Version="1.0" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/drstn_notifier/about.inc" VendorHomePage="http://www.axis.com" />
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.2-0" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" />
 <application Name="fenceguard" NiceName="AXIS Fence Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="47775" License="None" Status="Running" ConfigurationPage="local/fenceguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="loiteringguard" NiceName="AXIS Loitering Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="46775" License="None" Status="Running" ConfigurationPage="local/loiteringguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
 <application Name="motionguard" NiceName="AXIS Motion Guard" Vendor="Axis Communications" Version="2.2-6" ApplicationID="48170" License="None" Status="Running" ConfigurationPage="local/motionguard/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
</reply>"""
