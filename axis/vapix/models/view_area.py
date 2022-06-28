"""View area API data model."""

import attr

from .api import APIItem


@attr.s
class Geometry:
    """Represent a geometry object."""

    horizontalOffset: int = attr.ib()
    horizontalSize: int = attr.ib()
    verticalOffset: int = attr.ib()
    verticalSize: int = attr.ib()


@attr.s
class Size:
    """Represent a size object."""

    horizontal: int = attr.ib()
    vertical: int = attr.ib()


class ViewArea(APIItem):
    """View area object."""

    @property
    def source(self) -> int:
        """Image source that created view area."""
        return self.raw["source"]

    @property
    def camera(self) -> int:
        """View area used by streaming, PTZ and other APIs."""
        return self.raw["camera"]

    @property
    def configurable(self) -> bool:
        """Define if a view can be configured.

        Some view areas can not be configured and are thus unable to be changed
        with regards to geometry, etc.
        """
        return self.raw["configurable"]

    # These are only listed if the geometry of the view area can be configured.

    @property
    def canvas_size(self) -> Size:
        """Define size of the overview image that the view area geometry is defined on."""
        return Size(**self.raw["canvasSize"])

    @property
    def rectangular_geometry(self) -> Geometry:
        """Define a geometry for the view area as a rectangle related to the canvas."""
        return Geometry(**self.raw["rectangularGeometry"])

    @property
    def min_size(self) -> Size:
        """Define the minimum size that a view area can have."""
        return Size(**self.raw["minSize"])

    @property
    def max_size(self) -> Size:
        """Define the maximum size that a view area can have."""
        return Size(**self.raw["maxSize"])

    @property
    def grid(self) -> Geometry:
        """Define the grid that a geometry is applied to on the canvas due to device limitations."""
        return Geometry(**self.raw["grid"])
