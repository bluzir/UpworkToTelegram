import logging

import feedparser

from settings import UPWORK_FEED_URL


class RSSManager:
    url = UPWORK_FEED_URL

    def __init__(self):
        self.feed = None

    def parse_feed(self):
        try:
            feed = feedparser.parse(self.url)
            if feed['status'] == 200:
                self.feed = feed
        except Exception as e:
            logging.debug(e)