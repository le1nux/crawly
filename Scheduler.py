#!/usr/bin/env python3

import time
from WebsiteCrawler import due_job_queue
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Scheduler():
    def __init__(self, patterns):
        self.patterns = patterns
        self.known_urls = dict()
        self.add_known_urls(["", None])
        self.schedule_cond = threading.Condition()
        self.ap_scheduler = BackgroundScheduler()
        self.ap_scheduler.start()

    def schedule(self, article_link, feed_url, schedule_mode):
        # print("known urls size: ", sys.getsizeof(self.known_urls), " entries: ", len(self.known_urls.keys()))
        if article_link in self.known_urls:
            self.known_urls[article_link] = time.time()  # store last access time
        else:
            self.known_urls[article_link] = time.time()  # add link as key and store last access time
            last_scheduled_time = time.time() - self.patterns[0][1]     # subtract because first step in loop already adds the period
            with self.schedule_cond:
                if schedule_mode == 1:
                    for pattern in self.patterns:
                        for i in range(pattern[0]):
                            offset = pattern[1] + random.uniform(-5, 5)
                            run_date = datetime.fromtimestamp(last_scheduled_time + offset)

                            self.ap_scheduler.add_job(func=due_job_queue.put, trigger='date', args=([article_link, feed_url],),
                                                      run_date=run_date, misfire_grace_time=20)
                            last_scheduled_time = last_scheduled_time + pattern[1]
                    logger.debug("No. of scheduled jobs: %d", len(self.ap_scheduler.get_jobs()))
                elif schedule_mode == 2:
                    run_date = datetime.fromtimestamp(time.time())
                    self.ap_scheduler.add_job(func=due_job_queue.put, trigger='date', args=([article_link, feed_url],),
                                              run_date=run_date, misfire_grace_time=20)

    def add_known_urls(self, urls):
        list(map(lambda url: self.known_urls.update({url: time.time()}), urls))
