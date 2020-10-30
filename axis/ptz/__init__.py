""""""

from .ptz import *


class Ptz:
    def __init__(self, params, request):
        self._request = request
        self.control = None
        self.config = None
        self.focus = None
        self.speed_dry = None
