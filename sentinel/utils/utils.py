import threading
import time



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