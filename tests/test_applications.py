"""Test Axis Applications API.

pytest --cov-report term-missing --cov=axis.applications tests/test_applications.py
"""

from asynctest import Mock
import pytest

from axis.applications import Applications


@pytest.fixture
def applications() -> Applications:
    """Returns the api_discovery mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return Applications(mock_request)


def test_update_single_application(applications):
    """Test update applicatios call."""
    applications._request.return_value = list_application_response
    applications.update()
    applications._request.assert_called_with("post", "/axis-cgi/applications/list.cgi")

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


def test_update_multiple_applications(applications):
    """Test update applicatios call."""
    applications._request.return_value = list_applications_response
    applications.update()
    applications._request.assert_called_with("post", "/axis-cgi/applications/list.cgi")

    assert len(applications.values()) == 4

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


def test_list_single_application(applications):
    """Test list applicatios call."""
    applications._request.return_value = list_application_response
    raw = applications.list()
    applications._request.assert_called_with("post", "/axis-cgi/applications/list.cgi")

    assert "reply" in raw
    assert "application" in raw["reply"]
    assert raw["reply"]["application"]["@NiceName"] == "AXIS Video Motion Detection"


def test_list_multiple_applications(applications):
    """Test list applicatios call."""
    applications._request.return_value = list_applications_response
    raw = applications.list()
    applications._request.assert_called_with("post", "/axis-cgi/applications/list.cgi")

    assert "reply" in raw
    assert "application" in raw["reply"]
    assert raw["reply"]["application"][0]["@NiceName"] == "AXIS Remote Access solution"
    assert raw["reply"]["application"][1]["@NiceName"] == "AXIS Video Motion Detection"
    assert raw["reply"]["application"][2]["@NiceName"] == "AXIS Door Station Notifier"
    assert raw["reply"]["application"][3]["@NiceName"] == "AXIS Video Motion Detection"


list_application_response = b"""<reply result="ok">
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.4-5" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" LicenseName="Proprietary" />
</reply>"""

list_applications_response = b"""<reply result="ok">
 <application Name="RemoteAccess" NiceName="AXIS Remote Access solution" Vendor="Axis Communications" Version="1.12" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/RemoteAccess/#" VendorHomePage="http://www.axis.com" />
 <application Name="VMD3" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="3.2-1" ApplicationID="46396" License="None" Status="Stopped" ConfigurationPage="local/VMD3/setup.html" VendorHomePage="http://www.axis.com" />
 <application Name="drstn_notifier" NiceName="AXIS Door Station Notifier" Vendor="Axis Communications" Version="1.0" ApplicationID="1234" License="Custom" Status="Running" ConfigurationPage="local/drstn_notifier/about.inc" VendorHomePage="http://www.axis.com" />
 <application Name="vmd" NiceName="AXIS Video Motion Detection" Vendor="Axis Communications" Version="4.2-0" ApplicationID="143440" License="None" Status="Running" ConfigurationPage="local/vmd/config.html" VendorHomePage="http://www.axis.com" />
</reply>"""
