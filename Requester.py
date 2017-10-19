import requests
from time import gmtime, strftime
import logging
from Writer import writer_queue
import random
import string

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Requester:
    def __init__(self, tag, throttle, path="./dump/request_?.csv", log=True):
        self.log = log
        self.path = path
        self.tag = tag
        self.throttle = throttle

    def request(self, url, timeout):
        status = -1
        text = ""
        error = ""
        r = None
        try:
            self.throttle.get_pass(url) # blocks until URL is allowed to be accessed
            r = requests.get(url=url, timeout=timeout)
            #r.close()
        except Exception as err:
            logger.error("%s could not retrieve %s. Error: %s", self.tag, url, str(err))
            error = str(err)
        finally:
            if r:
                status = r.status_code
                text = r.text
            if self.log:
                line = [self.tag, url, text, status, error]
                self.write_log(line)
        return status, text

    def write_log(self, line):
        path = self.path.replace('?', strftime("%Y-%m-%d", gmtime()))
        job = {
            "path": path,
            "line": line
        }
        writer_queue.put(job)