"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.configuration tests/test_configuration.py
"""

from axis.configuration import Configuration


def test_configuration():
    """Test Configuration works."""
    config = Configuration(
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
