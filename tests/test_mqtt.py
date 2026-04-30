"""Test Axis MQTT Client API.

pytest --cov-report term-missing --cov=axis.mqtt tests/test_mqtt.py
"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from axis.interfaces.mqtt import MqttClientHandler, mqtt_json_to_event
from axis.models.mqtt import ClientConfig, Message, Server, ServerProtocol, Ssl

if TYPE_CHECKING:
    from axis.device import AxisDevice


@pytest.fixture
def mqtt_client(axis_device: AxisDevice) -> MqttClientHandler:
    """Return the mqtt_client mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.mqtt


async def _setup_mqtt_route(
    aiohttp_mock_server,
    mqtt_client: MqttClientHandler,
    path: str,
    response_json: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    _server, requests = await aiohttp_mock_server(
        path,
        method="POST",
        response=response_json if response_json is not None else {},
        device=mqtt_client,
        capture_payload=True,
    )
    return requests


async def test_client_config_simple(
    aiohttp_mock_server, mqtt_client: MqttClientHandler
):
    """Test simple MQTT client configuration."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/client.cgi"
    )

    client_config = ClientConfig(Server("192.168.0.1"))

    await mqtt_client.configure_client(client_config)

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/client.cgi"
    assert requests[-1]["payload"] == {
        "method": "configureClient",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "server": {"host": "192.168.0.1", "protocol": "tcp"},
        },
    }


async def test_client_config_advanced(
    aiohttp_mock_server, mqtt_client: MqttClientHandler
):
    """Test advanced MQTT client configuration."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/client.cgi"
    )

    client_config = ClientConfig(
        Server(
            "192.168.0.1",
            protocol=ServerProtocol.WS,
            alpn_protocol="alpn",
            basepath="base",
            port=1883,
        ),
        last_will_testament=Message(
            use_default=False,
            topic="LWT/client_1",
            message="client_1 LWT",
            retain=True,
            qos=1,
        ),
        connect_message=Message(
            use_default=False,
            topic="connected/client_1",
            message="client_1 connected",
            retain=False,
            qos=1,
        ),
        disconnect_message=Message(
            use_default=False,
            topic="disconnected/client_1",
            message="client_1 disconnected",
            retain=False,
            qos=1,
        ),
        ssl=Ssl(
            validate_server_cert=True,
            ca_cert_id="CA ID",
            client_cert_id="Client ID",
        ),
        activate_on_reboot=False,
        username="root",
        password="pass",
        client_id="client_1",
        keep_alive_interval=90,
        connect_timeout=90,
        clean_session=False,
        auto_reconnect=False,
    )

    await mqtt_client.configure_client(client_config)

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/client.cgi"
    assert requests[-1]["payload"] == {
        "method": "configureClient",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "server": {
                "host": "192.168.0.1",
                "port": 1883,
                "protocol": "ws",
                "alpnProtocol": "alpn",
                "basepath": "base",
            },
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
            "ssl": {
                "validateServerCert": True,
                "CACertID": "CA ID",
                "clientCertID": "Client ID",
            },
            "activateOnReboot": False,
            "clientId": "client_1",
            "keepAliveInterval": 90,
            "connectTimeout": 90,
            "cleanSession": False,
            "autoReconnect": False,
            "username": "root",
            "password": "pass",
        },
    }


async def test_activate_client(aiohttp_mock_server, mqtt_client: MqttClientHandler):
    """Test activate client method."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/client.cgi"
    )

    await mqtt_client.activate()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/client.cgi"
    assert requests[-1]["payload"] == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "activateClient",
    }


async def test_deactivate_client(aiohttp_mock_server, mqtt_client: MqttClientHandler):
    """Test deactivate client method."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/client.cgi"
    )

    await mqtt_client.deactivate()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/client.cgi"
    assert requests[-1]["payload"] == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "deactivateClient",
    }


async def test_get_client_status(aiohttp_mock_server, mqtt_client: MqttClientHandler):
    """Test get client status method."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server,
        mqtt_client,
        "/axis-cgi/mqtt/client.cgi",
        GET_CLIENT_STATUS_RESPONSE,
    )

    client_status = await mqtt_client.get_client_status()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/client.cgi"
    assert requests[-1]["payload"] == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "getClientStatus",
    }

    assert client_status.status.active is True
    assert client_status.status.connected is False


async def test_get_event_publication_config_small(
    aiohttp_mock_server, mqtt_client: MqttClientHandler
):
    """Test get event publication config method."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server,
        mqtt_client,
        "/axis-cgi/mqtt/event.cgi",
        {
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
                    "eventFilterList": [
                        {"topicFilter": "//.", "qos": 0, "retain": "none"}
                    ],
                }
            },
        },
    )

    response = await mqtt_client.get_event_publication_config()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/event.cgi"
    assert requests[-1]["payload"] == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "getEventPublicationConfig",
    }

    assert response.topic_prefix == "default"
    assert response.custom_topic_prefix == ""
    assert response.append_event_topic is True
    assert response.include_topic_namespaces is True
    assert response.include_serial_number_in_payload is False
    assert response.event_filter_list[0].topic_filter == "//."
    assert response.event_filter_list[0].qos == 0
    assert response.event_filter_list[0].retain == "none"

    assert response.to_dict() == {
        "topicPrefix": "default",
        "customTopicPrefix": "",
        "appendEventTopic": True,
        "includeTopicNamespaces": True,
        "includeSerialNumberInPayload": False,
        "eventFilterList": [{"topicFilter": "//.", "qos": 0, "retain": "none"}],
    }


async def test_configure_event_publication_all_topics(
    aiohttp_mock_server, mqtt_client: MqttClientHandler
):
    """Test configure event publication method with all topics."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/event.cgi"
    )

    await mqtt_client.configure_event_publication()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/event.cgi"
    assert requests[-1]["payload"] == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "configureEventPublication",
        "params": {"eventFilterList": [{"topicFilter": "//."}]},
    }


async def test_configure_event_publication_specific_topics(
    aiohttp_mock_server,
    mqtt_client: MqttClientHandler,
):
    """Test configure event publication method with specific topics."""
    requests = await _setup_mqtt_route(
        aiohttp_mock_server, mqtt_client, "/axis-cgi/mqtt/event.cgi"
    )

    topics = [
        "onvif:Device/axis:IO/VirtualPort",
        "onvif:Device/axis:Status/SystemReady",
        "axis:Storage//.",
    ]
    await mqtt_client.configure_event_publication(topics)

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/mqtt/event.cgi"
    assert requests[-1]["payload"] == {
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
    }


async def test_convert_json_to_event():
    """Verify conversion from json to event."""
    event = mqtt_json_to_event(
        b'{"timestamp": 1590045190230, "topic": "onvif:Device/axis:Sensor/PIR", "message": {"source": {"sensor": "0"}, "key": {}, "data": {"state": "0"}}}'
    )

    assert event == {
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }


def test_mqtt_json_to_event_missing_keys(caplog):
    """Test mqtt_json_to_event returns None and logs warning if keys are missing."""
    # Missing 'topic'
    msg = b'{"message": {"source": {"sensor": "0"}, "data": {"state": "0"}}}'
    result = mqtt_json_to_event(msg)
    assert result == {
        "topic": "",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }

    # Missing 'message' now returns dict with empty values
    msg = b'{"topic": "onvif:Device/axis:Sensor/PIR"}'
    result = mqtt_json_to_event(msg)
    assert result == {
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "",
        "source_idx": "",
        "type": "",
        "value": "",
    }

    # 'message' not a dict
    msg = b'{"topic": "onvif:Device/axis:Sensor/PIR", "message": 123}'
    result = mqtt_json_to_event(msg)
    assert result == {
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "",
        "source_idx": "",
        "type": "",
        "value": "",
    }


GET_CLIENT_STATUS_RESPONSE = {
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
