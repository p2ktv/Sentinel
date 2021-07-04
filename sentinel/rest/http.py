import asyncio
import weakref
import aiohttp
import sys
import json
import traceback
import logging
from urllib.parse import quote as _uriquote

from ..errors import HTTPException, Forbidden, NotFound, ServerError, SentinelError



log = logging.getLogger(__name__)
class Route:
    BASE = "https://discord.com/api/v9"

    def __init__(self, method, path, **kwargs):
        self.path = path
        self.method = method
        url = self.BASE + path
        if kwargs:
            self.url = url.format_map({x: _uriquote(y) if isinstance(y, str) else y for x, y in kwargs.items()})
        else:
            self.url = url

        self.channel_id = kwargs.get("channel_id")
        self.guild_id = kwargs.get("guild_id")
        self.webhook_id = kwargs.get("webhook_id")
        self.webhook_token = kwargs.get("webhook_token")

    
    @property
    def bucket(self):
        return "{}:{}:{}".format(self.channel_id, self.guild_id, self.path)


class MaybeUnlock:
    def __init__(self, lock):
        self.lock = lock
        self._unlock = True

    def __enter__(self):
        return self


    def defer(self):
        self._unlock = False

    def __exit__(self, type, value, traceback):
        if self._unlock:
            self.lock.release()


async def json_or_text(res):
    t = await res.text(encoding="utf-8")
    try:
        if res.headers["content-type"] == "application/json":
            return json.loads(t)
    except KeyError:
        pass
    return t


class HTTPClient:
    def __init__(self, ws, token):
        self.loop = asyncio.get_event_loop()
        self.ws = ws
        self.session = aiohttp.ClientSession()
        self._locks = weakref.WeakValueDictionary()
        self._token = token
        self.pool = None
        self._global_over = asyncio.Event()
        self._global_over.set()

        user_agent = 'DiscordBot ({0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format("0.0.1", sys.version_info, aiohttp.__version__)

    
    async def request(self, route, *, files=None, form=None, **kwargs):
        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        headers = {
            "User-Agent": self.user_agent,
            "Authorization": "Bot {}".format(self._token)
        }

        if "json" in kwargs:
            headers.update({
                "Content-Type": "application/json",
            })
            kwargs["data"] = json.dumps(kwargs.pop("json"))

        try:
            reason = kwargs.pop("reason")
        except KeyError:
            pass
        else:
            if reason:
                headers.update({
                    "X-Audit-Log-Reason": _uriquote(reason, safe="/ ")
                })

        kwargs.update({
            "headers": headers
        })

        if not self._global_over.is_set():
            await self._global_over.wait()

        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for t in range(5):
                if files:
                    for f in files:
                        f.reset(seek=t)
                
                if form:
                    f_data = aiohttp.FormData()
                    for p in form:
                        f_data.add_field(**p)
                    kwargs.update({
                        "data": f_data
                    })
                
                try:
                    async with self.session.request(method, url, **kwargs) as res:
                        data = await json_or_text(res)

                        r = res.headers.get("X-Ratelimit-Remaining", 1)
                        if int(r) == 0 and res.status != 429:
                            delta = float(res.headers.get("X-Ratelimit-Reset-After"))
                            maybe_lock.defer()
                            self.loop.call_later(delta, lock.release)
                        
                        if 300 > res.status >= 200:
                            return data

                        if res.status == 429:
                            if not res.headers.get("Via"):
                                raise HTTPException(res, data)
                            
                            txt = "Ratelimited! Retrying in {0} seconds (Bucket {1})"

                            retry_after = data["retry_after"]
                            log.warn(txt.format(retry_after, bucket))

                            _global = data.get("global", False)
                            if _global:
                                log.warn("Global rate limit hit!")
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)

                            if _global:
                                self._global_over.set()
                                log.info("Global ratelimit over.")
                            
                            continue
                
                        if res.status in (500, 502):
                            await asyncio.sleep(1 + t * 2)
                            continue
                    
                    if res.status == 403:
                        raise Forbidden(res, data)
                    elif res.status == 404:
                        raise NotFound(res, data)
                    elif res.status == 503:
                        raise ServerError(res, data)
                    else:
                        raise HTTPException(res, data)
            
                except OSError as e:
                    if t < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + t * 2)
                        continue
                    raise
            
            if res.status >= 500:
                raise ServerError(res, data)
            
            raise HTTPException(res, data)


    def send_message(self, channel_id, content, embeds: list =None):
        try:
            r = Route("POST", f"/channels/{channel_id}/messages", channel_id=channel_id)
            payload = {}

            if content:
                payload.update({
                    "content": content
                })

            final_embeds = []
            if embeds:
                for e in embeds:
                    final_embeds.append(e._to_json())
                payload.update({
                    "embeds": final_embeds
                })

            try:
                self.loop.run_until_complete(self.request(r, json=payload))
            except TimeoutError:
                pass
        except SentinelError as ex:
            log.error(ex)


    def get_guild_member(self, guild_id, user_id):
        try:
            r = Route("GET", f"/guilds/{guild_id}/members/{user_id}")
            
            res = self.loop.run_until_complete(self.request(r))
            return res
        except SentinelError as ex:
            log.error(ex)


    def get_guild_commands(self, guild_id, app_id):
        try:
            r = Route("GET", f"/applications/{app_id}/guilds/{guild_id}/commands")

            res = self.loop.run_until_complete(self.request(r))
            return res
        except SentinelError as ex:
            log.error(ex)


    def register_guild_command(self, guild_id: int, app_id: int, name: str, description: str, params: list):
        description = description if description != None else "A cool command!"
        try:
            payload = {
                "name": name,
                "description": description,
                "options": []
            }

            options = []
            if len(params) > 0:
                for i, p in enumerate(params):
                    options.append(
                        {
                            "name": p,
                            "description": f"Parameter number {i+1}",
                            "type": 3,
                            "required": True
                        }
                    )
                payload.update({
                    "options": options
                })
            
            r = Route("POST", f"/applications/{app_id}/guilds/{guild_id}/commands")

            res = self.loop.run_until_complete(self.request(r, json=payload))
            return res
        except SentinelError as ex:
            log.error(ex)


    def delete_guild_command(self, guild_id: int, app_id: int, command_id: int):
        try:
            r = Route("DELETE", f"/applications/{app_id}/guilds/{guild_id}/commands/{command_id}")

            res = self.loop.run_until_complete(self.request(r))
            return res
        except SentinelError as ex:
            log.error(ex)


    def respond_to_command(self, interaction_id: int, interaction_token: str, _type: int, content: str, embeds: list = None, flags = None):
        try:
            payload = {
                "type": _type,
                "data": {
                    "content": content,
                    "flags": flags
                }
            }
            final_embeds = []
            if embeds:
                for e in embeds:
                    final_embeds.append(e._to_json())
                payload["data"].update({
                    "embeds": final_embeds
                })
                
            r = Route("POST", f"/interactions/{interaction_id}/{interaction_token}/callback")

            res = self.loop.run_until_complete(self.request(r, json=payload))
            return res
        except SentinelError as ex:
            log.error(ex)


    def send_dm(self, user_id: int, content: str, embeds: list = None):
        try:
            dm_channel_payload = {
                "recipient_id": user_id
            }
            dm_req = Route("POST", f"/users/@me/channels")
            dm_channel = self.loop.run_until_complete(self.request(dm_req, json=dm_channel_payload))
            
            return self.send_message(dm_channel["id"], content, embeds)
        except SentinelError as ex:
            log.error(ex)


    def _delete_old_commands(self, commands: list, app_id: int):
        try:
            r = Route("GET", "/users/@me/guilds")

            guilds = self.loop.run_until_complete(self.request(r))
            for g in guilds:
                all_commands = self.get_guild_commands(g["id"], app_id)
                for cmd in all_commands:
                    if not cmd["name"].lower() in commands:
                        self.delete_guild_command(g["id"], app_id, cmd["id"])
        except SentinelError as ex:
            log.error(ex)