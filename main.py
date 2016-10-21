import shelve
from time import sleep

import feedparser
import requests

from settings import UPWORK_FEED_URL, TELEGRAM_BOT_TOKEN, CHAT_ID


class RSSManager:
    def __init__(self, url):
        self.url = url
        self.feed = None

    def parse_feed(self):
        try:
            feed = feedparser.parse(self.url)
            if feed['status'] == 200:
                self.feed = feed
        except Exception as e:
            print(e)


class JobManager:
    def __init__(self, rss, state):
        self.rss = rss
        self.state = state

    def check_new_jobs(self):
        last_id = self.state.get_value_from_key('last_link')
        if last_id:
            current_last_id = self.rss.feed['entries'][0]['link']
            if current_last_id == last_id:
                return False
            else:
                return True
        else:
            return True

    def get_new_jobs(self):
        if self.check_new_jobs:
            last_link = self.state.get_value_from_key('last_link')
            if last_link:
                jobs = self.rss.feed['entries']
                new_jobs = 0
                if jobs[0]['link'] == last_link:
                    print('No new jobs, sleeping 30 seconds')
                    sleep(30)
                else:
                    for job in jobs:
                        if job['link'] != last_link:
                            new_jobs += 1
                        else:
                            print('Got new jobs: {}'.format(new_jobs))
                            return jobs[:new_jobs]
                print('Got new jobs: {}'.format(new_jobs))
                return jobs[:new_jobs]
            else:
                return reversed(self.rss.feed['entries'])
        else:
            print('No new jobs, sleeping 30 seconds')
            sleep(30)
            return []


class Job:
    def __init__(self, job_title, job_link):
        self.title = job_title
        self.link = job_link


class TelegramAPIManager:
    telegram_bot_api_url = 'https://api.telegram.org/bot{}/{}'
    parse_mode = 'markdown'
    chat_id = CHAT_ID
    token = TELEGRAM_BOT_TOKEN
    params = {
            'chat_id': chat_id,
            'parse_mode': parse_mode,
    }

    def send_message(self, text):
        self.params.update({'text': text})
        full_url = self.telegram_bot_api_url.format(TELEGRAM_BOT_TOKEN, 'sendMessage')
        response = requests.get(url=full_url, params=self.params)
        decode = response.json()
        if decode['ok']:
            print('Successfully sent message to channel')
            sleep(3)


class TelegramJobPoster(TelegramAPIManager):
    def __init__(self, job, states):
        self.job = job
        self.states = states
        self.formatted = None

    def format_job_to_message(self):
        self.formatted = "{}\n[Cсылка]({})\n".format(self.job.title, self.job.link)

    def post_job(self):
        if not self.formatted:
            self.format_job_to_message()
        self.send_message(self.formatted)
        self.states.add_value_by_key('last_link', self.job.link)


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
            d.close()
            return value
        else:
            d.close()
            return False


def main():
    my_states = StateManager('states')
    my_upwork_feed = RSSManager(UPWORK_FEED_URL)
    my_upwork_feed.parse_feed()
    my_jobs = JobManager(my_upwork_feed, my_states)
    while True:
        jobs = my_jobs.get_new_jobs()
        if jobs:
            for job in jobs:
                new_job = Job(job['title'], job['link'])
                TelegramJobPoster(new_job, my_states).post_job()


if __name__ == '__main__':
    main()