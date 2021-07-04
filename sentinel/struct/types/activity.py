


class Activity:
    def __init__(self, _type: int, name: str):
        self._type = _type
        self.name = name


    def _to_json(self):
        return {
            "type": self._type,
            "name": self.name
        }