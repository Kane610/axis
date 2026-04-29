"""Test Axis Basic Device Info API.

pytest --cov-report term-missing --cov=axis.basic_device_info tests/test_basic_device_info.py
"""

from unittest.mock import MagicMock

import aiohttp
from aiohttp import web

from axis.device import AxisDevice
from axis.models.configuration import Configuration

from .conftest import HOST, PASS, USER


async def test_get_all_properties(aiohttp_server):
    """Test get all properties api."""
    requests: list[dict[str, object]] = []

    async def handle_basic_device_info(request: web.Request) -> web.Response:
        payload = await request.json()
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": payload,
            }
        )
        return web.json_response(GET_ALL_PROPERTIES_RESPONSE)

    app = web.Application()
    app.router.add_post("/axis-cgi/basicdeviceinfo.cgi", handle_basic_device_info)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=server.port,
            username=USER,
            password=PASS,
        )
    )
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.get().version = "1.0"
    basic_device_info = axis_device.vapix.basic_device_info

    try:
        await basic_device_info.update()
    finally:
        await session.close()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/basicdeviceinfo.cgi"
    assert requests[-1]["payload"] == {
        "method": "getAllProperties",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert basic_device_info.initialized

    device_info = basic_device_info["0"]
    assert device_info.architecture == "armv7hf"
    assert device_info.brand == "AXIS"
    assert device_info.build_date == "Apr 29 2020 06:50"
    assert device_info.firmware_version == "9.80.1"
    assert device_info.hardware_id == "70E"
    assert device_info.product_full_name == "AXIS M1065-LW Network Camera"
    assert device_info.product_number == "M1065-LW"
    assert device_info.product_short_name == "AXIS M1065-LW"
    assert device_info.product_type == "Network Camera"
    assert device_info.product_variant == ""
    assert device_info.serial_number == "ACCC12345678"
    assert device_info.soc == "Ambarella S2L (Flattened Device Tree)"
    assert device_info.soc_serial_number == ""
    assert device_info.web_url == "http://www.axis.com"


async def test_get_supported_versions(aiohttp_server):
    """Test get supported versions api."""
    requests: list[dict[str, object]] = []

    async def handle_basic_device_info(request: web.Request) -> web.Response:
        payload = await request.json()
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": payload,
            }
        )
        return web.json_response(
            {
                "apiVersion": "1.1",
                "context": "Axis library",
                "method": "getSupportedVersions",
                "data": {"apiVersions": ["1.1"]},
            }
        )

    app = web.Application()
    app.router.add_post("/axis-cgi/basicdeviceinfo.cgi", handle_basic_device_info)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=server.port,
            username=USER,
            password=PASS,
        )
    )
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.get().version = "1.0"
    basic_device_info = axis_device.vapix.basic_device_info

    try:
        response = await basic_device_info.get_supported_versions()
    finally:
        await session.close()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/basicdeviceinfo.cgi"
    assert requests[-1]["payload"] == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.1"]


GET_ALL_PROPERTIES_RESPONSE = {
    "apiVersion": "1.1",
    "context": "Axis library",
    "method": "getAllProperties",
    "data": {
        "propertyList": {
            "Architecture": "armv7hf",
            "ProdNbr": "M1065-LW",
            "HardwareID": "70E",
            "Version": "9.80.1",
            "ProdFullName": "AXIS M1065-LW Network Camera",
            "Brand": "AXIS",
            "ProdType": "Network Camera",
            "Soc": "Ambarella S2L (Flattened Device Tree)",
            "SocSerialNumber": "",
            "WebURL": "http://www.axis.com",
            "ProdVariant": "",
            "SerialNumber": "ACCC12345678",
            "ProdShortName": "AXIS M1065-LW",
            "BuildDate": "Apr 29 2020 06:50",
        }
    },
}
