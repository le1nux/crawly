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
pip install requirements.txt
```

Start _crawly_:
```bash
python3 Starter.py configs/your_config.txt
```


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
