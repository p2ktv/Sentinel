import logging

from ..struct.types import Context
from ..errors import SentinelError



log = logging.getLogger(__name__)
def slash_handler(ws, payload):
    name = payload["data"].get("name", None)
    passed_params = payload["data"].get("options", [])
    if name is None:
        return
    if name in ws.commands:
        func = ws.commands[name]["func"]
        bot = ws.commands[name]["kwargs"]
        args = []
        if len(ws.commands[name]["params"]) > 0:
            for e in passed_params:
                if e["name"] in ws.commands[name]["params"]:
                    args.append(e["value"])
        
        try:
            func(Context(payload, bot.get("bot"), ws.commands[name]["flags"]), *args)
        except SentinelError as ex:
            log.error(ex)