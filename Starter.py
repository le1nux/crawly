import logging
from logging.handlers import TimedRotatingFileHandler

from Writer import Writer
from Crawler import Crawler
from Throttle import Throttle
from Requester import Requester
from Scheduler import Scheduler
from WebsiteCrawler import DownloadWorker
import time
import configparser
import sys
import threading
import psutil
import os
from pathlib import Path


def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = './configs/config_default.txt'

    if not Path(config_path).is_file():
        logging.error("Could not find config file!")
        sys.exit(1)     # exiting with error code

    # load config
    config = configparser.ConfigParser()
    config.read(config_path)


    log_dir = config['PATHS']['log_dir']

    # check if config dir is present
    if not Path(log_dir).is_dir():
        logging.error("Logging directory is not present!")
        sys.exit(1)     # exiting with error code

    file_handler = TimedRotatingFileHandler(os.path.join(os.path.dirname(__file__), log_dir, 'logs'), when='midnight', interval=1)
    console_handler = logging.StreamHandler()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[file_handler, console_handler])

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)
    logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
    logging.getLogger("chardet.charsetprober").setLevel(logging.WARNING)


    logger.info("=======Starting=Crawler=========")

    # store config preferences in variables
    article_download_pattern = ([(int(config['ARTICLE_DOWNLOAD_PATTERN']['number']), int(config['ARTICLE_DOWNLOAD_PATTERN']['delay'])),])   # [(application number, period in seconds) ... ]
    number_download_worker = int(config['CRAWLING']['number_download_worker'])
    website_request_timeout = int(config['REQUESTS']['website_request_timeout'])
    rss_feed_crawl_period = int(config['CRAWLING']['rss_feed_crawl_period'])
    rss_feed_request_timeout = int(config['REQUESTS']['rss_feed_request_timeout'])
    warmup_iterations = int(config['CRAWLING']['warmup_iterations'])
    throttle_velocity = float(config['CRAWLING']['throttle_velocity'])
    downloads_path = config['PATHS']['downloads']
    crawled_rss_articles_path = config['PATHS']['rss_articles']
    feed_path = config['PATHS']['feeds_list']
    requests_path = config['PATHS']['requests']

    # partly validating the config
    if not Path(feed_path).is_file():
        logging.error("Could not find RSS feeds list file!")
        sys.exit(1)     # exiting with error code

    requests_file_path = Path(requests_path)
    if not Path(os.path.dirname(requests_file_path)).is_dir():
        logging.error("Could not find requests directory!")
        sys.exit(1)     # exiting with error code

    writer = Writer()
    writer.start()

    throttle = Throttle(request_velocity=throttle_velocity)

    rss_requester = Requester(tag="RSS Requester", path=requests_path, throttle=throttle)
    website_requester = Requester(tag="Website Requester", path=requests_path, throttle=throttle)

    scheduler = Scheduler(patterns=article_download_pattern)

    crawler = Crawler(requester=rss_requester, scheduler=scheduler, feed_path=feed_path,
                      crawled_rss_articles_path=crawled_rss_articles_path,
                      rss_feed_crawl_period=rss_feed_crawl_period, rss_feed_request_timeout=rss_feed_request_timeout,
                      warmup_iterations=warmup_iterations)
    crawler.start()

    for i in range(number_download_worker):
        logger.info("Starting download worker #%d", i)
        DownloadWorker(requester=website_requester, timeout=website_request_timeout, path=downloads_path).start()

    while True:
        time.sleep(60)
        logger.debug("Number of threads running: %d", threading.active_count())
        process = psutil.Process(os.getpid())
        ram_usage = process.memory_full_info()
        # percent = absolute/mem.total
        logger.info("RAM usage: %s%%,  %s", process.memory_percent(), ram_usage)

if __name__ == "__main__":
    main()
