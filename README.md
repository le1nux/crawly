# Crawly
... a crawler that retrieves news articles via RSS feeds.

# Description
_Crawly_ retrieves RSS feeds in a pre-defined interval and checks whether there are any new RSS items present. 
If so it immediately downloads the news articles referred to in the new RSS items (link tag).

Since some articles may be modified / corrected later on, _crawly_ can download articles in a fixed interval for a fixed number of times. 


# Getting started

Clone the repository
```bash
git clone https://github.com/le1nux/crawly.git
```
and create the following directories: 
```bash
cd crawly
mkdir logs
mkdir resources
mkdir dump
```
Install the [required packages](https://github.com/le1nux/crawly/blob/master/requirements.txt) by running
```bash
cd crawly
pip install -r requirements.txt
```

Start _crawly_:
```bash
python3 Starter.py configs/your_config.txt
```

If you are using the default config the crawler will run two warmup runs in the beginning where it collects all RSS items and marks them as 'known'. Afterwards it will download the RSS feeds in pre-set intervals and check whether there are new items in the RSS feeds. If so it will download the corresponding articles every 10mins for one hour (7 times in total) and store them in website_downloads_<current_date>.csv. Also see section Article Storage. 


# Configuration
_crawly_ comes with a sane [default configuration](https://github.com/le1nux/crawly/blob/master/configs/config_default.txt). To set up feeds to crawl, set the path accordingly:
```python
# Path to feeds list
feeds_list = ./resources/example_feed_list.csv
```

If you keep the default configuration, _crawly_ will retrieve all RSS feeds in 3-minute intervals and download new articles every 10 mins for 1 hour (-> 7 times in total).

**IMPORTANT** 

All temporal settings are in seconds.
Always keep defensive crawling intervals; preferably in the minutes area.

# Article Storage
This section assumes that you are using the default config. 
There are three files in ./dump used for data storage:

* **request_<current_date>.csv** backup of all requests 

* **crawled_articles<current_date>.csv** all RSS feed items are stored here

* **website_downloads_<current_date>.csv** all article downloads are stored here

#### request_<current_date>.csv
Each HTTP request (RSS feed request or article download) is stored as a row in request_<current_date>.csv. Each row has the following row format:

```
request module, url, html_content
```
request_<current_date>.csv is not meant for your analysis and rather a backup of all requests. 

#### crawled_articles<current_date>.csv
In each iteration step (after the two warmup steps) all RSS items in the RSS feeds are stored in this file. There is no check for already existing items in place so the file usually contains each RSS item multiple times. 
The CSV file format is as follows:

```
timestamp_retrieved, outlet_name, outlet_url, article_link, title, description, timestamp_published
```
The last three columns are directly extracted from the RSS item itself. See [here](https://en.wikipedia.org/wiki/RSS#Example) for an example RSS item. 


#### website_downloads_<current_date>.csv
This file contains the articles downloaded from the outlet website and has the following CSV file format:

```
timestamp_retrieved, link_to_article, html_download
```
# Suggested Reading

* RSS Feed format: [Wikipedia RSS](https://en.wikipedia.org/wiki/RSS)

* Extracting text from HTML: [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

* Working with CSV files: [Pandas CSV import](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html)

# License

MIT License

Copyright (c) 2017 le1nux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
