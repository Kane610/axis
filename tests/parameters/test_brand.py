"""Test Axis brand parameter management."""

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.parameters.brand import BrandParameterHandler

from ..conftest import HOST

BRAND_RESPONSE = """root.Brand.Brand=AXIS
root.Brand.ProdFullName=AXIS M1065-LW Network Camera
root.Brand.ProdNbr=M1065-LW
root.Brand.ProdShortName=AXIS M1065-LW
root.Brand.ProdType=Network Camera
root.Brand.ProdVariant=
root.Brand.WebURL=http://www.axis.com"""


@pytest.fixture
def brand_handler(axis_device: AxisDevice) -> BrandParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.brand_handler


@respx.mock
async def test_brand_handler(brand_handler: BrandParameterHandler):
    """Verify that update brand works."""
    route = respx.post(
        f"http://{HOST}:80/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.Brand"},
    ).respond(
        text=BRAND_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    await brand_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert brand_handler.supported
    brand = brand_handler["0"]
    assert brand.brand == "AXIS"
    assert brand.product_full_name == "AXIS M1065-LW Network Camera"
    assert brand.product_number == "M1065-LW"
    assert brand.product_short_name == "AXIS M1065-LW"
    assert brand.product_type == "Network Camera"
    assert brand.product_variant == ""
    assert brand.web_url == "http://www.axis.com"
