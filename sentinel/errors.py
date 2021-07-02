


class SentinelError(Exception):
    """Base exception for all errors raised by the Sentinel library

    That indeed means cathing class:`~sentinel.errors.SentinelError` can
    be used to handle any error in this package
    """
    pass


class HTTPException(SentinelError):
    def __init__(self, res, msg):
        self.res = res
        self.msg = msg
        if isinstance(msg, dict):
            self.code = msg.get("code", 0)
            base = msg.get("message", "")
            errors = msg.get("errors")
            if errors:
                self.text = "\n".join([f"{x} : {y}" for x, y in errors.items()])
            else:
                self.text = base

        else:
            self.text = msg
            self.code = 0

        txt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            txt += ": {2}"

        super().__init__(txt.format(self.res, self.code, self.text))


class Forbidden(HTTPException):
    """Excpetion for status code 403"""
    pass


class NotFound(HTTPException):
    """Excpetion for status code 404"""
    pass


class ServerError(HTTPException):
    """Excpetion for status code in range 500"""
    pass