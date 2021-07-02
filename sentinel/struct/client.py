import asyncio
import concurrent
import logging
from functools import wraps

from ..rest.ws import WebSocket
from ..rest.http import HTTPClient
from ..errors import SentinelError



log = logging.getLogger(__name__)
valid_listeners = [
    "message_create",
    "ready"
]
class SentinelClient:
    def __init__(self, token, app_id):
        self.intents = 513
        self.pool = concurrent.futures.ProcessPoolExecutor(2)
        self.loop = asyncio.get_event_loop()
        self._ws = WebSocket()
        self._http = HTTPClient(self._ws, token)
        self._ws.pool = self.pool
        self._http.pool = self.pool
        self.token = token
        self.prefix = "/"
        self.commands = {}
        self.categories = {}
        self.listeners = {}
        self.tasks = []
        self.app_id = app_id


    def build(self):
        try:
            self._ws.connect(self, self.token, self.intents)
        except KeyboardInterrupt:
            quit()
        except SentinelError as ex:
            self.loop.stop()
            log.error(ex)
        else:
            return self



    def set_user(self):
        self.id = self._ws.id
        self.name = self._ws.username
        self.discriminator = self._ws.discriminator



    def send(self, channel_id, content):
        self._http.send_message(channel_id, content)


    def get_member(self, guild_id, user_id):
        return self._http.get_guild_member(guild_id, user_id)



    @property
    def latency(self):
        return round(self._ws.latency * 1000)

    

    def slash_command(self, name: str, guild_id: int, description: str = "A cool command!", category: str = "default"):
        def dec(func, name=name, category=category, description=description):
            name = name.lower()
            category = category.lower()
            if name in self.commands:
                raise SentinelError("Command with that name already exists")
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self.commands.update({
                name: {
                    "category": category,
                    "description": description,
                    "func": wrapper,
                    "kwargs": {"bot": self}
                }
            })
            if not category in self.categories:
                self.categories.update({
                    category: [self.commands[name]]
                })
            else:
                self.categories[category].append(self.commands[name])
            self._ws.commands = self.commands

            setattr(self, name, wrapper)

            self._register_command(guild_id, name, description)

            return func
        return dec


    def _register_command(self, guild_id: int, name: str, description: str = "A cool command!"):
        try:
            commands = self._http.get_guild_commands(guild_id, self.app_id)
        except SentinelError:
            raise
        else:
            for cmd in commands:
                if cmd["name"].lower() not in self.commands:
                    self._http.delete_guild_command(guild_id, self.app_id, cmd["id"])

            if name not in [i["name"].lower() for i in commands]:
                self._http.register_guild_command(guild_id, self.app_id, name, description)
            else:
                pass