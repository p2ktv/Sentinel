import logging

from ..struct.types import Context
from ..errors import SentinelError



log = logging.getLogger(__name__)
def slash_handler(ws, payload):
    name = payload["data"].get("name", None)
    if name is None:
        return
    if name in ws.commands:
        func = ws.commands[name]["func"]
        kwargs = ws.commands[name]["kwargs"]
        try:
            func(Context(payload, kwargs.get("bot")))
        except SentinelError as ex:
            log.error(ex)