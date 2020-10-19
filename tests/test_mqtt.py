"""Test Axis MQTT Client API.

pytest --cov-report term-missing --cov=axis.mqtt tests/test_mqtt.py
"""
import pytest
from unittest.mock import AsyncMock

from axis.mqtt import (
    ClientConfig,
    Server,
    Message,
    Ssl,
    MqttClient,
    mqtt_json_to_event,
)


@pytest.fixture
def mqtt_client() -> MqttClient:
    """Returns the mqtt_client mock object."""
    mock_request = AsyncMock()
    mock_request.return_value = ""
    return MqttClient(mock_request)


async def test_client_config_simple(mqtt_client):
    """Test simple MQTT client configuration."""
    client_config = ClientConfig(Server("192.168.0.1"))

    await mqtt_client.configure_client(client_config)
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        json={
            "method": "configureClient",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": {
                "server": {"host": "192.168.0.1", "port": 1883, "protocol": "tcp"},
                "lastWillTestament": {"useDefault": True},
                "connectMessage": {"useDefault": True},
                "disconnectMessage": {"useDefault": True},
                "ssl": {"validateServerCert": False},
                "activateOnReboot": True,
                "clientId": "",
                "keepAliveInterval": 60,
                "connectTimeout": 60,
                "cleanSession": True,
                "autoReconnect": True,
            },
        },
    )


async def test_client_config_advanced(mqtt_client):
    """Test advanced MQTT client configuration."""
    client_config = ClientConfig(
        Server("192.168.0.1"),
        lastWillTestament=Message(
            useDefault=False,
            topic="LWT/client_1",
            message="client_1 LWT",
            retain=True,
            qos=1,
        ),
        connectMessage=Message(
            useDefault=False,
            topic="connected/client_1",
            message="client_1 connected",
            retain=False,
            qos=1,
        ),
        disconnectMessage=Message(
            useDefault=False,
            topic="disconnected/client_1",
            message="client_1 disconnected",
            retain=False,
            qos=1,
        ),
        ssl=Ssl(validateServerCert=True),
        activateOnReboot=False,
        username="root",
        password="pass",
        clientId="client_1",
        keepAliveInterval=90,
        connectTimeout=90,
        cleanSession=False,
        autoReconnect=False,
    )

    await mqtt_client.configure_client(client_config)
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        json={
            "method": "configureClient",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": {
                "server": {"host": "192.168.0.1", "port": 1883, "protocol": "tcp"},
                "lastWillTestament": {
                    "useDefault": False,
                    "topic": "LWT/client_1",
                    "message": "client_1 LWT",
                    "retain": True,
                    "qos": 1,
                },
                "connectMessage": {
                    "useDefault": False,
                    "topic": "connected/client_1",
                    "message": "client_1 connected",
                    "retain": False,
                    "qos": 1,
                },
                "disconnectMessage": {
                    "useDefault": False,
                    "topic": "disconnected/client_1",
                    "message": "client_1 disconnected",
                    "retain": False,
                    "qos": 1,
                },
                "ssl": {"validateServerCert": True},
                "activateOnReboot": False,
                "clientId": "client_1",
                "keepAliveInterval": 90,
                "connectTimeout": 90,
                "cleanSession": False,
                "autoReconnect": False,
                "username": "root",
                "password": "pass",
            },
        },
    )


async def test_activate_client(mqtt_client):
    """Test activate client method."""
    await mqtt_client.activate()
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "activateClient",
            "params": {},
        },
    )


async def test_deactivate_client(mqtt_client):
    """Test deactivate client method."""
    await mqtt_client.deactivate()
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "deactivateClient",
            "params": {},
        },
    )


async def test_get_client_status(mqtt_client):
    """Test get client status method."""
    await mqtt_client.get_client_status()
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getClientStatus",
            "params": {},
        },
    )


async def test_get_event_publication_config(mqtt_client):
    """Test get event publication config method."""
    await mqtt_client.get_event_publication_config()
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getEventPublicationConfig",
        },
    )


async def test_configure_event_publication_all_topics(mqtt_client):
    """Test configure event publication method with all topics."""
    await mqtt_client.configure_event_publication()
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "configureEventPublication",
            "params": {"eventFilterList": [{"topicFilter": "//."}]},
        },
    )


async def test_configure_event_publication_specific_topics(mqtt_client):
    """Test configure event publication method with specific topics."""
    topics = [
        "onvif:Device/axis:IO/VirtualPort",
        "onvif:Device/axis:Status/SystemReady",
        "axis:Storage//.",
    ]
    await mqtt_client.configure_event_publication(topics)
    mqtt_client._request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "configureEventPublication",
            "params": {
                "eventFilterList": [
                    {"topicFilter": "onvif:Device/axis:IO/VirtualPort"},
                    {"topicFilter": "onvif:Device/axis:Status/SystemReady"},
                    {"topicFilter": "axis:Storage//."},
                ]
            },
        },
    )


async def test_convert_json_to_event():
    event = mqtt_json_to_event(
        b'{"timestamp": 1590045190230, "topic": "onvif:Device/axis:Sensor/PIR", "message": {"source": {"sensor": "0"}, "key": {}, "data": {"state": "0"}}}'
    )

    assert event["operation"] == "Changed"
    assert event["topic"] == "tns1:Device/tnsaxis:Sensor/PIR"
    assert event["source"] == "sensor"
    assert event["source_idx"] == "0"
    assert event["type"] == "state"
    assert event["value"] == "0"


response_get_client_status = {
    "apiVersion": "1.0",
    "context": "some context",
    "method": "getClientStatus",
    "data": {
        "status": {"state": "active", "connectionStatus": "Connected"},
        "config": {
            "activateOnReboot": True,
            "server": {"protocol": "tcp", "host": "192.168.0.90", "port": 1883},
            "clientId": "client_1",
            "keepAliveInterval": 60,
            "connectTimeout": 60,
            "cleanSession": True,
            "autoReconnect": True,
            "lastWillTestament": {
                "useDefault": False,
                "topic": "LWT/client_1",
                "message": "client_1 LWT",
                "retain": True,
                "qos": 1,
            },
            "connectMessage": {
                "useDefault": False,
                "topic": "connected/client_1",
                "message": "client_1 connected",
                "retain": False,
                "qos": 1,
            },
            "disconnectMessage": {
                "useDefault": False,
                "topic": "disconnected/client_1",
                "message": "client_1 disconnected",
                "retain": False,
                "qos": 1,
            },
            "ssl": {"validateServerCert": False},
        },
    },
}

response_get_event_publication_config = {
    "apiVersion": "1.0",
    "context": "Axis lib",
    "method": "getEventPublicationConfig",
    "data": {
        "eventPublicationConfig": {
            "topicPrefix": "default",
            "customTopicPrefix": "",
            "appendEventTopic": True,
            "includeTopicNamespaces": True,
            "includeSerialNumberInPayload": False,
            "eventFilterList": [{"topicFilter": "//.", "qos": 0, "retain": "none"}],
        }
    },
}
