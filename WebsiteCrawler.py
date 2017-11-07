#!/usr/bin/env python3

from threading import Thread
from queue import Queue
import time
import logging
from Writer import writer_queue
from time import gmtime, strftime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

due_job_queue = Queue()


class DownloadWorker(Thread):
    def __init__(self, requester, timeout, path):
        super(DownloadWorker, self).__init__()
        self.timeout = timeout
        self.requester = requester
        self.path = path

    def run(self):
        logger.info("DownloadWorker started...")
        while True:
            article_url, feed_url = due_job_queue.get()
            #logger.debug("due_job_queue size: %s", due_job_queue.qsize())
            status_code, content = self.requester.request(url=article_url, timeout=self.timeout)
            if status_code == 200:
                logger.debug("Retrieved article %s", article_url)
                download = [time.time(), article_url, feed_url, content]
                job = {
                    "path": self.path.replace('?', strftime("%Y-%m-%d", gmtime())),
                    "line": download
                }
                writer_queue.put(job)