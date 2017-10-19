from queue import Queue
from threading import Thread
import csv
import codecs
import logging

writer_queue = Queue()  # job format: {"path": path, "line": ["some_url", "bla bla", "test123"]}
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Writer(Thread):
    def __init__(self):
        super(Writer, self).__init__()
        self.open_files = dict()

    def run(self):
        while True:
            job = writer_queue.get()
            #logger.debug("writer_queue size: %s", writer_queue.qsize())
            self.write(job["path"], job["line"])

    def write(self, path, line):
        try:
            if path in self.open_files:
                file = self.open_files[path]
            else:
                file = open(path, 'a', encoding="utf-8")
                self.open_files[path] = file
            wr = csv.writer(file, quoting=csv.QUOTE_ALL)
            wr.writerow([codecs.encode(str(e), 'unicode_escape').decode('utf-8') for e in line])
            file.flush()
        except Exception as err:
            logger.error("Could not write to %s Error: %s", path, str(err))

# when reading this stuff later on...
# def read():
#     with open('./dump/test.csv', newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
#         for row in reader:
#             print([r.encode('utf-8').decode('unicode_escape') for r in row])or r in row])