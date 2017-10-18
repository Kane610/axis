# python3 -m axis

import asyncio

from axis import AxisDevice
from functools import partial


loop = asyncio.get_event_loop()

port = 8080
event_list = ['motion']
kw = {'host': '10.0.1.51',
      'username': 'root',
      'password': 'pass',
      'port': port,
      'events': event_list}

loop.call_soon(partial(AxisDevice, loop, **kw))
loop.run_forever()
loop.close()
