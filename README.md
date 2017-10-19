# Crawly
... a crawler that retrieves news articles via RSS feeds.

# Description
_Crawly_ retrieves RSS feeds in a pre-defined interval and checks whether there are any new RSS items present. 
If so it immediately downloads the news articles referred to in the new RSS items (link tag).

Since some articles may be modified / corrected later on, _crawly_ can download articles in a fixed interval for a fixed number of times. 


# Getting started
Clone the repository 
```bash
git clone git@github.com:le1nux/crawly.git
```
After having installed the required python packages (see ) and having configured crawly (see ) you can run *crawly* 

```bash
python3 Starter.py configs/your_config.txt
```

# Requirements

Install the [required packages](https://github.com/le1nux/crawly/requirements.txt) by running

```bash
cd foo/bar/crawly
pip install requirements.txt
```

# Configuration
You can leave all the preferences as they are defined in the [template](https://github.com/le1nux/crawly/configs/config_default.txt) except for

```python
# Path to feeds list
feeds_list = ./resources/feeds_list.csv
```
which must have the correct path to your feeds list. 

If you keep the template's preferences *crawly* will retrieve all RSS feeds in 3 minutes intervals and download new articles every 10 mins for 1 hour (-> 7 times in total).

IMPORTANT: 

All temporal settings are in seconds.
Always keep defensive crawling intervals preferably in the minutes area.


