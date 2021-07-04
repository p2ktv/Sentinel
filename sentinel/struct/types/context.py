from .user import User



class Context:
    def __init__(self, payload, bot, flags, _type=4):
        self.bot = bot
        self._token = payload["token"]
        self._id = payload["id"]
        self._type = _type
        self.flags = flags
        self.channel_id = payload["channel_id"]
        self.message_id = payload["data"]["id"]
        self.author = User(payload)


    def respond(self, content: str, embeds: list = None):
        message = self.bot._http.respond_to_command(
            self._id, 
            self._token, 
            self._type, 
            content,
            embeds,
            flags=self.flags
        )
        return message


    def dm(self, content: str):
        message = self.bot._http.send_dm(
            self.author["user"]["id"],
            content
        )
        return message
