import shelve
from time import sleep

import feedparser
import requests

from settings import UPWORK_FEED_URL, TELEGRAM_BOT_TOKEN


class RSSManager:
    def __init__(self, url, state):
        self.url = url
        self.state = state
        self.feed = None

    def parse_feed_by_url(self):
        try:
            feed = feedparser.parse(self.url)
            if feed['status'] == 200:
                self.feed = feed
        except Exception as e:
            print(e)

    def check_new_jobs(self):
        old_pubdate = self.state.get_value_from_key('pubdate')
        new_pubdate = self.feed['feed']['published']
        if old_pubdate == new_pubdate:
            return False
        else:
            last_id = self.state.get_value_from_key('last_id')
            if last_id:
                current_last_id = self.feed['entries'][0]['id']
                if current_last_id == last_id:
                    return False
                else:
                    return True

    def get_new_jobs(self):
        if self.check_new_jobs:
            last_id = self.state.get_value_from_key('last_id')
            jobs = self.feed['entries']
            new_jobs = 0
            for job in jobs:
                if job['id'] != last_id:
                    new_jobs += 1
                else:
                    return jobs[:new_jobs]
        else:
            return []


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
        sleep(5)


class StateManager:
    def __init__(self, file):
        self.file = file

    def add_value_by_key(self, key, value):
        d = shelve.open(self.file)
        d[key] = value
        d.close()

    def get_value_from_key(self, key):
        d = shelve.open(self.file)
        if key in d:
            value = d[key]
            return value
        else:
            return False


def main():
    state = StateManager('states')
    my_upwork_feed = RSSManager(UPWORK_FEED_URL, state)
    my_telegram = TelegramAPIManager(-1001024228888)
    my_upwork_feed.parse_feed_by_url()
    while True:
        jobs = my_upwork_feed.get_new_jobs()
        if jobs:
            print('Got new jobs: {}'.format(len(jobs)))
            for job in jobs:
                title, published, link = job['title'], job['published'], job['link']
                new_job = Job(title, published, link)
                new_job.format_job_to_message()
                my_telegram.send_message(new_job.formatted)
                state.add_value_by_key('last_id', job['id'])
        else:
            print('No new jobs, sleeping 30 seconds')
            sleep(30)


if __name__ == '__main__':
    main()