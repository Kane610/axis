"""Transport protocol shared by stream implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .rtsp import State


class StreamSession(Protocol):
    """Session contract for stream transports."""

    @property
    def state(self) -> State:
        """Current stream state."""


class StreamTransport(Protocol):
    """Minimal transport contract used by StreamManager."""

    @property
    def session(self) -> StreamSession:
        """Underlying transport session."""

    async def start(self) -> None:
        """Start receiving stream data."""

    def stop(self) -> None:
        """Stop receiving stream data."""

    @property
    def data(self) -> bytes | dict[str, Any]:
        """Return latest stream payload."""
