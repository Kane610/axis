"""MQTT Client api."""

from typing import Any

from ..models.api_discovery import ApiId
from ..models.mqtt import (
    API_VERSION,
    ActivateClientRequest,
    ClientConfig,
    ClientConfigStatus,
    ConfigureClientRequest,
    ConfigureEventPublicationRequest,
    DeactivateClientRequest,
    EventFilter,
    EventPublicationConfig,
    GetClientStatusRequest,
    GetClientStatusResponse,
    GetEventPublicationConfigRequest,
    GetEventPublicationConfigResponse,
)
from .api_handler import ApiHandler

DEFAULT_TOPICS = ["//."]


class MqttClientHandler(ApiHandler[Any]):
    """MQTT Client for Axis devices."""

    api_id = ApiId.MQTT_CLIENT
    default_api_version = API_VERSION

    async def configure_client(self, client_config: ClientConfig) -> None:
        """Configure MQTT Client."""
        await self.vapix.api_request(
            ConfigureClientRequest(
                api_version=self.default_api_version, client_config=client_config
            )
        )

    async def activate(self) -> None:
        """Activate MQTT Client."""
        await self.vapix.api_request(
            ActivateClientRequest(api_version=self.default_api_version)
        )

    async def deactivate(self) -> None:
        """Deactivate MQTT Client."""
        await self.vapix.api_request(
            DeactivateClientRequest(api_version=self.default_api_version)
        )

    async def get_client_status(self) -> ClientConfigStatus:
        """Get MQTT Client status."""
        bytes_data = await self.vapix.api_request(
            GetClientStatusRequest(api_version=self.default_api_version)
        )
        response = GetClientStatusResponse.decode(bytes_data)
        return response.data

    async def get_event_publication_config(self) -> EventPublicationConfig:
        """Get MQTT Client event publication config."""
        bytes_data = await self.vapix.api_request(
            GetEventPublicationConfigRequest(api_version=self.default_api_version)
        )
        response = GetEventPublicationConfigResponse.decode(bytes_data)
        return response.data

    async def configure_event_publication(
        self, topics: list[str] = DEFAULT_TOPICS
    ) -> None:
        """Configure MQTT Client event publication."""
        event_filters = EventFilter.from_list(
            [{"topicFilter": topic} for topic in topics]
        )
        config = EventPublicationConfig(event_filter_list=event_filters)
        await self.vapix.api_request(
            ConfigureEventPublicationRequest(
                api_version=self.default_api_version, config=config
            )
        )
