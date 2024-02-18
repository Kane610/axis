"""Test Axis Applications API.

pytest --cov-report term-missing --cov=axis.applications.applications tests/applications/test_applications.py
"""

import pytest

from axis.vapix.interfaces.applications import ApplicationsHandler


@pytest.fixture
def applications(axis_device) -> ApplicationsHandler:
    """Return the applications mock object."""
    return axis_device.vapix.applications


async def test_update_no_application(respx_mock, applications: ApplicationsHandler):
    """Test update applicatios call."""
    route = respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=LIST_APPLICATION_EMPTY_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )

    await applications.update()

    assert route.called
    assert len(applications.values()) == 0


async def test_update_single_application(respx_mock, applications: ApplicationsHandler):
    """Test update applications call."""
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=LIST_APPLICATION_RESPONSE,
        headers={"Content-Type": "text/xml"},
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
    respx_mock, applications: ApplicationsHandler
):
    """Test update applicatios call."""
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=LIST_APPLICATIONS_RESPONSE,
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
