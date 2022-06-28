"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

from typing import Any, Optional

from .api import APIItem


class Param(APIItem):
    """Parameter group."""

    def __contains__(self, obj_id: str) -> bool:
        """Evaluate object membership to parameter group."""
        return obj_id in self.raw

    def get(self, obj_id: str, default: Optional[Any] = None) -> Any:
        """Get object if stored in raw else return default."""
        return self.raw.get(obj_id, default)

    def __getitem__(self, obj_id: str) -> Any:
        """Return Param[obj_id]."""
        return self.raw[obj_id]
