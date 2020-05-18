"""Test Axis MQTT Client API.

pytest --cov-report term-missing --cov=axis.mqtt tests/test_mqtt.py
"""

from asynctest import Mock

from axis.mqtt import ClientConfig, DEFAULT_TOPICS, Server, Message, Ssl, MqttClient


def test_mqtt():
    """Test MQTT Client API works."""
    mock_request = Mock()
    mock_request.return_value = ""
    mqtt_client = MqttClient({}, mock_request)

    client_config = ClientConfig(
        Server("192.168.0.1"),
        lastWillTestament=Message(),
        connectMessage=Message(),
        disconnectMessage=Message(),
        ssl=Ssl(),
    )

    mqtt_client.configure_client(client_config)
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        data={
            "method": "configureClient",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": {
                "server": {"host": "192.168.0.1", "port": 1883, "protocol": "tcp"},
                "lastWillTestament": {
                    "useDefault": True,
                    "topic": None,
                    "message": None,
                    "retain": None,
                    "qos": None,
                },
                "connectMessage": {
                    "useDefault": True,
                    "topic": None,
                    "message": None,
                    "retain": None,
                    "qos": None,
                },
                "disconnectMessage": {
                    "useDefault": True,
                    "topic": None,
                    "message": None,
                    "retain": None,
                    "qos": None,
                },
                "ssl": {"validateServerCert": False},
                "activateOnReboot": True,
                "username": None,
                "password": None,
                "clientId": "",
                "keepAliveInterval": 60,
                "connectTimeout": 60,
                "cleanSession": True,
                "autoReconnect": True,
            },
        },
    )

    mqtt_client.activate()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        data={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "activateClient",
        },
    )

    mqtt_client.deactivate()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        data={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "deactivateClient",
        },
    )

    mqtt_client.get_client_status()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/client.cgi",
        data={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getClientStatus",
        },
    )

    mqtt_client.get_event_publication_config()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        data={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getEventPublicationConfig",
        },
    )

    mqtt_client.configure_event_publication()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        data={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "configureEventPublication",
            "params": {"eventFilterList": [{"topicFilter": "//."}]},
        },
    )

    topics = [
        "onvif:Device/axis:IO/VirtualPort",
        "onvif:Device/axis:Status/SystemReady",
        "axis:Storage//.",
    ]
    mqtt_client.configure_event_publication(topics)
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/mqtt/event.cgi",
        data={
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


client_status_response = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "method": "getClientStatus",
    "data": {
        "status": {"state": "inactive", "connectionStatus": "Not connected"},
        "config": {
            "activateOnReboot": True,
            "server": {"protocol": "tcp", "host": "192.168.0.1", "port": 1883},
            "clientId": "client_1",
            "keepAliveInterval": 60,
            "connectTimeout": 60,
            "cleanSession": True,
            "autoReconnect": True,
            "lastWillTestament": {"useDefault": True},
            "connectMessage": {"useDefault": True},
            "disconnectMessage": {"useDefault": True},
            "ssl": {"validateServerCert": False},
        },
    },
}


event_publication_config_response = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "method": "getEventPublicationConfig",
    "data": {
        "eventPublicationConfig": {
            "topicPrefix": "",
            "customTopicPrefix": "",
            "appendEventTopic": True,
            "includeTopicNamespaces": True,
            "includeSerialNumberInPayload": False,
            "eventFilterList": [],
        }
    },
}


{
    "apiVersion": "1.0",
    "context": "some context",
    "method": "configureClient",
    "params": {
        "activateOnReboot": True,
        "server": {"protocol": "tcp", "host": "192.168.0.1", "port": 1883},
        "clientId": "client_1",
        "cleanSession": True,
        "lastWillTestament": {"useDefault": True},
        "connectMessage": {"useDefault": True},
        "disconnectMessage": {"useDefault": True},
        "ssl": {"validateServerCert": False},
    },
}


{
    "apiVersion": "1.0",
    "context": "some context",
    "method": "configureClient",
    "params": {
        "activateOnReboot": True,
        "server": {
            "protocol": "wss",
            "host": "broker-address",
            "port": 443,
            "basepath": "url-extension",
        },
        "username": "username",
        "password": "password",
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
        "ssl": {"validateServerCert": True},
    },
}
