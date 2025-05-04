"""Test Axis brand parameter management."""

import pytest

from axis.device import AxisDevice
from axis.interfaces.parameters.brand import BrandParameterHandler

BRAND_RESPONSE = """root.Brand.Brand=AXIS
root.Brand.ProdFullName=AXIS M1065-LW Network Camera
root.Brand.ProdNbr=M1065-LW
root.Brand.ProdShortName=AXIS M1065-LW
root.Brand.ProdType=Network Camera
root.Brand.ProdVariant=
root.Brand.WebURL=http://www.axis.com"""

BRAND_5_51_RESPONSE = """root.Brand.Brand=AXIS
root.Brand.ProdFullName=AXIS M3024-L Network Camera
root.Brand.ProdShortName=AXIS M3024-L
root.Brand.ProdNbr=M3024-L
root.Brand.ProdType=Network Camera
root.Brand.WebURL=http://www.axis.com/
"""


@pytest.fixture
def brand_handler(axis_device: AxisDevice) -> BrandParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.brand_handler


async def test_brand_handler(respx_mock, brand_handler: BrandParameterHandler):
    """Verify that update brand works."""
    route = respx_mock.post(
        "/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.Brand"},
    ).respond(
        content=BRAND_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    assert not brand_handler.initialized

    await brand_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert brand_handler.initialized
    brand = brand_handler["0"]
    assert brand.brand == "AXIS"
    assert brand.product_full_name == "AXIS M1065-LW Network Camera"
    assert brand.product_number == "M1065-LW"
    assert brand.product_short_name == "AXIS M1065-LW"
    assert brand.product_type == "Network Camera"
    assert brand.product_variant == ""
    assert brand.web_url == "http://www.axis.com"


async def test_brand_handler_5_51(respx_mock, brand_handler: BrandParameterHandler):
    """Verify that update brand works."""
    respx_mock.post(
        "/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.Brand"},
    ).respond(
        content=BRAND_5_51_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    await brand_handler.update()

    assert brand_handler.initialized
    brand = brand_handler["0"]
    assert brand.brand == "AXIS"
    assert brand.product_full_name == "AXIS M3024-L Network Camera"
    assert brand.product_number == "M3024-L"
    assert brand.product_short_name == "AXIS M3024-L"
    assert brand.product_type == "Network Camera"
    assert brand.product_variant == ""
    assert brand.web_url == "http://www.axis.com/"
