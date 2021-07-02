


class Embed:
    def __init__(self, color=0xffffff, title="", description=""):
        self.color = color
        self.title = title
        self.description = description
        self._thumbnail = {}
        self.fields = []


    def thumbnail(self, url: str, proxy_url=None, height=512, width=512):
        self._thumbnail = {
            "url": url,
            "proxy_url": proxy_url,
            "height": height,
            "width": width
        }


    def field(self, name: str, value: str, inline=False):
        self.fields.append(
            {
                "name": name,
                "value": value,
                "inline": inline
            }
        )
        

    def _to_json(self):
        return {
            "color": self.color,
            "title": self.title,
            "description": self.description,
            "thumbnail": self._thumbnail,
            "fields": self.fields
        }