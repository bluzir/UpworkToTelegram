import shelve
from time import sleep

import feedparser
import requests

from settings import UPWORK_FEED_URL, TELEGRAM_BOT_TOKEN, CHAT_ID


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
                    print('Got new jobs: {}'.format(len(new_jobs)))
                    return jobs[:new_jobs]
        else:
            print('No new jobs, sleeping 30 seconds')
            return []


class Job:
    def __init__(self, job_title, job_published, job_link, telegram, states):
        self.title = job_title
        self.datetime = job_published
        self.link = job_link
        self.telegram = telegram
        self.states = states
        self.formatted = None

    def format_job_to_message(self):
        self.formatted = "{}\n[Cсылка]({})\n".format(self.title, self.link)

    def post_job(self):
        if not self.formatted:
            self.format_job_to_message()
        self.telegram.send_message(self.formatted)
        self.states.add_value_by_key('last_id', self.job['id'])


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
    my_states = StateManager('states')
    my_upwork_feed = RSSManager(UPWORK_FEED_URL, my_states)
    my_telegram = TelegramAPIManager(CHAT_ID)
    my_upwork_feed.parse_feed_by_url()
    while True:
        jobs = my_upwork_feed.get_new_jobs()
        if jobs:
            for job in jobs:
                new_job = Job(job['title'], job['published'], job['link'], my_telegram, my_states)
                new_job.post_job()
        else:
            sleep(30)


if __name__ == '__main__':
    main()