"""Test Axis stream profiles API.

pytest --cov-report term-missing --cov=axis.stream_profiles tests/test_stream_profiles.py
"""

import pytest
from unittest.mock import Mock

from axis.stream_profiles import StreamProfiles


@pytest.fixture
def stream_profiles() -> StreamProfiles:
    """Returns the stream_profiles mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return StreamProfiles(mock_request)


def test_list_stream_profiles(stream_profiles):
    """Test get_supported_versions"""
    stream_profiles._request.return_value = response_list
    stream_profiles.update()
    stream_profiles._request.assert_called_with(
        "post",
        "/axis-cgi/streamprofile.cgi",
        json={
            "method": "list",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": {"streamProfileName": []},
        },
    )

    assert len(stream_profiles.values()) == 1

    stream_profile = stream_profiles["My full HD profile"]
    assert stream_profile.id == "My full HD profile"
    assert stream_profile.name == "My full HD profile"
    assert stream_profile.description == "HD profile:1920x1080"
    assert stream_profile.parameters == "resolution=1920x1080"


def test_get_supported_versions(stream_profiles):
    """Test get_supported_versions"""
    stream_profiles._request.return_value = response_getSupportedVersions
    response = stream_profiles.get_supported_versions()
    stream_profiles._request.assert_called_with(
        "post", "/axis-cgi/streamprofile.cgi", json={"method": "getSupportedVersions"},
    )
    assert response["data"] == {"apiVersions": ["1.0"]}


response_list = {
    "method": "list",
    "apiVersion": "1.0",
    "data": {
        "streamProfile": [
            {
                "name": "My full HD profile",
                "description": "HD profile:1920x1080",
                "parameters": "resolution=1920x1080",
            }
        ],
        "maxProfiles": 26,
    },
}


response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
