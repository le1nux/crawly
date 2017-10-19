
import threading
import time
from threading import Timer
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Throttle():
    def __init__(self, request_velocity):
        self.request_velocity = request_velocity
        self.domain_dict = dict()
        self.modify_cond = threading.Condition() # only one thread is allowed to modify domain_dict at a time

    def get_pass(self, url):
        domain = urlparse(url).netloc
        with self.modify_cond:
            if domain not in self.domain_dict:
                e = threading.Event()
                self.domain_dict[domain] = [0, 0, time.time(), threading.Condition(), e, None]  # [delay, counter, date created, mutex, event, timer]
                e.set()     # wake all thead that are waiting for this domain

        with self.domain_dict[domain][3]:         # only one thread is allowed to send to that url at a time
            self.domain_dict[domain][4].wait()    # wait that the timer sets e
            self.domain_dict[domain][4].clear()   # set e back to false
            # the timer sets the event to true such that another thread waiting for it can
            # can send the next request
            timer = Timer(self.request_velocity, self.domain_dict[domain][4].set)
            self.domain_dict[domain][5] = timer
            timer.start()
           # when this function call is passed it means that the url can now be requested



