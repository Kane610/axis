"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.configuration tests/test_configuration.py
"""

from httpx import AsyncClient

from axis.models.configuration import Configuration


def test_configuration():
    """Test Configuration works."""
    session = AsyncClient(verify=False)
    config = Configuration(
        session,
        "192.168.0.1",
        username="root",
        password="pass",
        port=443,
        web_proto="https",
        verify_ssl=True,
    )

    assert config.host == "192.168.0.1"
    assert config.username == "root"
    assert config.password == "pass"
    assert config.port == 443
    assert config.web_proto == "https"
    assert config.verify_ssl is True
    assert config.url == "https://192.168.0.1:443"


def test_minimal_configuration():
    """Test Configuration works."""
    session = AsyncClient(verify=False)
    config = Configuration(
        session,
        "192.168.1.1",
        username="bill",
        password="cipher",
    )

    assert config.host == "192.168.1.1"
    assert config.username == "bill"
    assert config.password == "cipher"
    assert config.port == 80
    assert config.web_proto == "http"
    assert config.verify_ssl is False
    assert config.url == "http://192.168.1.1:80"
