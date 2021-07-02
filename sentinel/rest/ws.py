import asyncio
import websocket
import json
import threading
import time
import logging

from ..utils.constants import Constants, OPCodes
from ..utils.payloads import Identify, Heartbeat
from ..utils.utils import setInterval
from ..handlers import slash_handler
from .http import HTTPClient
from ..errors import SentinelError



log = logging.getLogger(__name__)
event = threading.Event()
logging.basicConfig(level=logging.INFO, format="[{levelname:<7}] - {message}", style="{")
valid_events = [
    "interaction_create",
    "ready"
]
class WebSocket:
    def __init__(self):
        self.socket = None
        self.interval = None
        self.loop = asyncio.get_event_loop()
        self._token = None
        self.pool = None
        self.commands = {}
        self.categories = {}
        self.listeners = {}
        self.client = None
        self._log = logging.getLogger(__name__)

        self.latency = None
        self.last_heartbeat = None
        self.last_heartbeat_ack = None

        self.discriminator = None
        self.id = None
        self.username = None


    def send_payload(self, payload: str):
        self.socket.send(json.dumps(payload))


    def receive_payload(self):
        try:
            payload = self.socket.recv()
            if payload is not None and payload != "None":
                return json.loads(payload)
        except SentinelError as ex:
            log.error(ex)
            self.socket.connect(Constants.GATEWAY_URL)


    def connect(self, client, token: str, intents: int):
        try:
            self.socket = websocket.WebSocket()
            self.socket.connect(Constants.GATEWAY_URL)
        except SentinelError as ex:
            log.error(ex)
            self.socket.connect(Constants.GATEWAY_URL)
        else:
            self.client = client
            self._token = token
            self.interval = self.receive_payload()["d"]["heartbeat_interval"]
            self._http = HTTPClient(self, self._token)

            Identify["d"].update({"token": token, "intents": 13967})
            self.send_payload(Identify)

            s2 = setInterval(
                self.listen,
                event,
                1
            )
            s2.start()

            def heartbeat():
                self.send_payload(Heartbeat)
                self.last_heartbeat = time.time()
            s = setInterval(
                heartbeat,
                event,
                self.interval / 1000
            )
            s.start()


    def listen(self):
        try:
            payload = self.receive_payload()
            if payload["t"] is not None:
                event = payload["t"].lower()
                if event == "interaction_create":
                    slash_handler(self, payload["d"])
                elif event == "ready":
                    self._log.info(f"Client is now online!")
                
            
            if payload["op"] == OPCodes.ELEVEN:
                self.last_heartbeat_ack = time.time()
                if self.last_heartbeat is not None and self.last_heartbeat_ack is not None:
                    self.latency = self.last_heartbeat_ack - self.last_heartbeat

            elif payload["op"] == OPCodes.ZERO:
                if "user" in payload["d"]:
                    for k, v in payload["d"]["user"].items():
                        setattr(self, k, v)
                    self.client.set_user()
        except SentinelError as ex:
            log.error(ex)