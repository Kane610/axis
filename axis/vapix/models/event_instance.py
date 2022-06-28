"""Event service and action service APIs available in Axis network device."""

from typing import Union

from .api import APIItem


class EventInstance(APIItem):
    """Events are emitted when the Axis product detects an occurrence of some kind.

    For example motion in camera field of view or a change of status from an I/O port.
    The events can be used to trigger actions in the Axis product or in other systems
    and can also be stored together with video and audio data for later access.
    """

    @property
    def topic(self) -> str:
        """Event topic.

        Event declaration namespae.
        """
        return self.raw["topic"]

    @property
    def topic_filter(self) -> str:
        """Event topic.

        Event topic filter namespae.
        """
        return self.raw["topic"].replace("tns1", "onvif").replace("tnsaxis", "axis")

    @property
    def is_available(self) -> bool:
        """Means the event is available."""
        return self.raw["data"]["@topic"] == "true"

    @property
    def is_application_data(self) -> bool:
        """Indicate event and/or data is produced for specific system or application.

        Events with isApplicationData=true are usually intended
        to be used only by the specific system or application, that is,
        they are not intended to be used as triggers in an action rule in the Axis product.
        """
        return self.raw["data"].get("@isApplicationData") == "true"

    @property
    def name(self) -> str:
        """User-friendly and human-readable name describing the event."""
        return self.raw["data"].get("@NiceName", "")

    @property
    def stateful(self) -> bool:
        """Stateful event is a property (a state variable) with a number of states.

        The event is always in one of its states.
        Example: The Motion detection event is in state true when motion is detected
        and in state false when motion is not detected.
        """
        return self.raw["data"]["MessageInstance"].get("@isProperty") == "true"

    @property
    def stateless(self) -> bool:
        """Stateless event is a momentary occurrence (a pulse).

        Example: Storage device removed.
        """
        return self.raw["data"]["MessageInstance"].get("@isProperty") != "true"

    @property
    def source(self) -> Union[dict, list]:
        """Event source information."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("SourceInstance", {}).get("SimpleItemInstance", {})

    @property
    def data(self) -> Union[dict, list]:
        """Event data description."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("DataInstance", {}).get("SimpleItemInstance", {})
