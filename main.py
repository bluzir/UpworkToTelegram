import feedparser
import requests

from settings import UPWORK_FEED_URL, TELEGRAM_BOT_TOKEN


class RSSManager:

    def __init__(self, url):
        self.url = url
        self.feed = None

    def parse_feed_by_url(self):
        try:
            feed = feedparser.parse(self.url)
            if feed['status'] == 200:
                self.feed = feed['entries']
        except Exception as e:
            print(e)

    def parse_jobs_from_feed(self):
        pass


class Job:

    def __init__(self, job_title, job_published, job_link):
        self.title = job_title
        self.datetime = job_published
        self.link = job_link
        self.formatted = None

    def post_job(self):
        print(self.formatted)

    def format_job_to_message(self):
        self.formatted = "{}\n[Cсылка]({})\n".format(self.title, self.link)


class TelegramAPIManager:
    telegram_bot_api_url = 'https://api.telegram.org/bot{}/{}'
    parse_mode = 'markdown'

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.token = TELEGRAM_BOT_TOKEN
        self.params = {
            'chat_id': self.chat_id,
            'parse_mode': self.parse_mode,
        }

    def send_message(self, text):
        self.params.update({'text': text})
        full_url = self.telegram_bot_api_url.format(TELEGRAM_BOT_TOKEN, 'sendMessage')
        response = requests.get(url=full_url,
                                params=self.params)
        print(response.json())



my_upwork_feed = RSSManager(UPWORK_FEED_URL)
my_telegram = TelegramAPIManager(-1001024228888)
my_upwork_feed.parse_feed_by_url()
if my_upwork_feed.feed:
    jobs = my_upwork_feed.feed
    for job in jobs:
        title, published, link = job['title'], job['published'], job['link']
        new_job = Job(title, published, link)
        new_job.format_job_to_message()
        my_telegram.send_message(new_job.formatted)



