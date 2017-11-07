import pandas as pd
import logging
import hashlib
import time
import threading
import feedparser
import random
from dateutil import parser as date_parser
from Writer import writer_queue
from time import gmtime, strftime
from threading import Thread

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Crawler(Thread):
    def __init__(self, requester, scheduler, feed_path="./resources/news_feeds.csv", crawled_rss_articles_path="./dump/crawled_articles_?.csv",
                 rss_feed_crawl_period=300, rss_feed_request_timeout=5, warmup_iterations=3, max_offset=0):
        super(Crawler, self).__init__()
        self.requester = requester
        self.feed_path = feed_path
        self.crawled_rss_articles_path = crawled_rss_articles_path
        self.rss_feed_crawl_period = rss_feed_crawl_period  # in seconds
        self.rss_feed_request_timeout = rss_feed_request_timeout
        self.scheduler = scheduler
        self.outlet_crawlers = []
        self.warmup_iterations = warmup_iterations
        # This is the maximum time in seconds that an outlet crawler can be delayed.
        # Each OutletCrawler is now being delayed by a random number between [0, max_offset] such that
        # DNS and the network itself does not get overwhelmed when the Crawler starts a crawling iteration step.
        # NOTE: max_offset must be less than (<<) the duration of iteration step!
        self.max_offset = max_offset

    def update_feeds(self, feeds_all, old_hash):
        try:
            new_hash = hashlib.md5(open(self.feed_path, 'rb').read()).hexdigest()
        except Exception as err:
            logger.error("Could not get hash for %s, Error: ", self.feed_path, str(err))
            return [], None

        if new_hash is None:
            logger.error("new_hash is None")
            return [], None
        elif new_hash != old_hash:
            logging.info("Feeds file was modified. updating ...")
            feeds_all = pd.read_csv(self.feed_path)
            logging.info("Feeds updated.")
            return feeds_all, new_hash
        return feeds_all, new_hash

    def run(self):
        self.doWarmup(self.warmup_iterations)
        self.crawl()

    def doWarmup(self, iterations):
        next_crawl = time.time()
        feeds_df = None
        old_hash = None
        for i in range(iterations):
            logger.info("Running warmup %d/%d", i + 1, iterations)
            feeds_df, old_hash = self.update_feeds(feeds_df, old_hash)
            logger.info("Retrieving %s RSS feeds...", feeds_df["feed_url"].count())
            self.crawl_outlets(feeds_df, warmup=True)
            next_crawl = next_crawl + self.rss_feed_crawl_period
            delay = next_crawl - time.time()
            logger.info("Warmup %d/%d done.", i + 1, iterations)
            logger.info("Next run is in %.2fs.", delay)
            time.sleep(delay)

    def crawl(self):
        next_crawl = time.time()
        feeds_df = None
        old_hash = None
        while True:
            feeds_df, old_hash = self.update_feeds(feeds_df, old_hash)
            logger.info("Retrieving %s RSS feeds...", feeds_df["feed_url"].count())
            self.crawl_outlets(feeds_df, warmup=False)
            next_crawl = next_crawl + self.rss_feed_crawl_period
            delay = next_crawl - time.time()
            logger.info("Next run is in %.2fs.", delay)
            time.sleep(delay)

    def crawl_outlets(self, feeds_all, warmup=False):
        list(map(lambda crawler: crawler.stop(), self.outlet_crawlers))
        self.outlet_crawlers = []
        grouped_feeds = feeds_all.groupby(['outlet'], axis=0)
        for outlet_name, feeds_outlet in grouped_feeds:
            logger.debug("Crawling %s", outlet_name)
            offset = random.random() * self.max_offset
            outlet_crawler = OutletCrawler(outlet_name=outlet_name,
                                           feeds=feeds_outlet,
                                           scheduler=self.scheduler,
                                           requester=self.requester,
                                           rss_feed_request_timeout=self.rss_feed_request_timeout,
                                           crawled_rss_articles_path=self.crawled_rss_articles_path,
                                           warmup=warmup,
                                           offset=offset)
            self.outlet_crawlers.append(outlet_crawler)
            outlet_crawler.start()

class OutletCrawler(Thread):
    def __init__(self, outlet_name, feeds, scheduler, requester, rss_feed_request_timeout, crawled_rss_articles_path, warmup=False, offset=0):
        super(OutletCrawler, self).__init__()
        self._stop_event = threading.Event()
        self.outlet_name = outlet_name
        self.feeds = feeds
        self.scheduler = scheduler
        self.requester = requester
        self.warmup = warmup
        self.crawled_rss_articles_path = crawled_rss_articles_path
        self.rss_feed_request_timeout = rss_feed_request_timeout
        self.offset = offset

    def run(self):
        time.sleep(self.offset)
        logger.debug("offset sleeping for %.2fs done", self.offset)
        if self.warmup:
            self.doWarmup()
        else:
            self.crawl_outlet()
        self._stop_event.set()

    def doWarmup(self):
        logger.info("Crawling %s's feeds...", self.outlet_name)
        for index, feed in self.feeds.iterrows():
            if self.stopped():
                logger.warning("Outletcrawler %s was stopped from outside.", self.outlet_name)
                return
            else:
                feed_url = feed["feed_url"]
                articles = self.get_feed(feed_url)
                urls = [article[3] for article in articles]
                self.scheduler.add_known_urls(urls)
        logger.info("Crawling %s's feeds done", self.outlet_name)

    def crawl_outlet(self):
        logger.info("Crawling %s's feeds...", self.outlet_name)
        for index, feed in self.feeds.iterrows():
            if self.stopped():
                logger.warning("Outletcrawler %s was stopped from outside.", self.outlet_name)
                return
            else:
                feed_url = feed["feed_url"]
                articles = self.get_feed(feed_url)
                list(map(lambda article: self.scheduler.schedule(article[3], feed_url, schedule_mode=int(feed[4])), articles))
                list(map(lambda article : writer_queue.put(
                    {
                        "path": self.crawled_rss_articles_path.replace('?', strftime("%Y-%m-%d", gmtime())),
                        "line": article
                    }
                ), articles))
        logger.info("Crawling %s's feeds done", self.outlet_name)

    def get_feed(self, feed_url):
        articles = []
        logger.debug("Retrieving %s" % (feed_url,))
        status_code, content = self.requester.request(feed_url, self.rss_feed_request_timeout)
        if status_code == 200:
            logger.debug("Retrieval of %s returned HTTP Code %d", feed_url, status_code)
            try:
                feed = feedparser.parse(content)
            except Exception as err:
                logger.error("Could not parse content from %s, Error: %s", feed_url, str(err))
                return articles
            entries = feed["entries"]
            for entry in entries:
                try:
                    pub_date = date_parser.parse(entry["published"]).timestamp() if "published" in entry else 0
                except ValueError:
                    logger.error("Could not parse %s (feed = %s)", entry["published"], feed_url)
                    pub_date = 0
                link = entry["link"] if "link" in entry else ""
                title = entry["title"] if "title" in entry else ""
                summary = entry["summary"] if "summary" in entry else ""

                articles.append([time.time(), self.outlet_name, feed_url, link, title, summary, pub_date])
        else:
            logger.warning("Retrieval of %s returned HTTP Code %d" % (feed_url, status_code))
        return articles

    def stop(self):
        logger.debug("Stop of OutletCrawler %s  called ...", self.outlet_name)
        if not self.stopped():
            logger.warning("Stopping OutletCrawler %s ...", self.outlet_name)
            self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()