import threading
import time
import inspect



class setInterval(threading.Thread):
    def __init__(self, callback, event, interval: int):
        self.callback = callback
        self.event = event
        self.interval = interval
        super(setInterval, self).__init__()


    def run(self, *args, **kwargs):
        while True:
            self.callback()
            time.sleep(self.interval)


def get_command_params(wrapper):
    sig = inspect.signature(wrapper)
    params = {}
    for n, p in sig.parameters.items():
        an = p.annotation
        if n is not None:
            params[n] = an
    params = list(params.keys())
    return params[1:] if len(params) > 0 else []