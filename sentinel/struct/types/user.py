


class User:
    def __init__(self, payload):
        self._raw_payload = payload
        for k, v in payload["member"].items():
            if k == "user":
                for _k, _v in v.items():
                    setattr(self, _k, _v)
            else:
                if not k == "avatar":
                    setattr(self, k, v)
        
        self.avatar = f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size=512" # now this is the direct url, tho online as a png
        self.ping = f"<@!{self.id}>"


    def __repr__(self):
        return f"{self.username}#{self.discriminator}"