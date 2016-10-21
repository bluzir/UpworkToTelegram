# -*- coding:utf-8 -*-

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

    def new_jobs_available(self):
        last_link = self.state.get_value_from_key('last_link')

        if last_link is False:
            return True

        current_last_link = self.rss.feed['entries'][0]['link']
        if current_last_link == last_link:
            return False
        else:
            return True

    def get_new_jobs(self):
        if not self.new_jobs_available():
            return []

        last_link = self.state.get_value_from_key('last_link')

        if not last_link:
            jobs = self.rss.feed['entries']
            self.state.add_value_by_key('last_link', jobs[0].link)
            return Job.create_from_list(jobs)

        jobs = self.rss.feed['entries']
        new_jobs = 0
        for job in jobs:
            if job['link'] != last_link:
                new_jobs += 1
            else:
                print('Find new jobs: {}'.format(new_jobs))
                self.state.add_value_by_key('last_link', jobs[0].link)
                jobs = jobs[:new_jobs]
                return Job.create_from_list(jobs)


class Job:
    def __init__(self, job_title, job_link):
        self._set_title(job_title)
        self.link = job_link

    def _set_title(self, title):
        postfix = " - Upwork"
        postfix_position = title.rfind(postfix)
        if postfix_position != -1:
            title = title[0:postfix_position]

        self.title = title

    @staticmethod
    def create_from_list(job_list):
        jobs = []
        for job in job_list:
            job = Job(job["title"], job["link"])
            jobs.append(job)

        return jobs


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
    # feed = FeedClient(feed_link)
    # telegram = TelegramJobPoster()
    #
    # for job in feed.get_new_jobs():
    #     telegram.post(job)


    ###
    my_states = StateManager('states')
    my_upwork_feed = RSSManager(UPWORK_FEED_URL)
    my_upwork_feed.parse_feed()
    my_jobs = JobManager(my_upwork_feed, my_states)
    while True:
        jobs = my_jobs.get_new_jobs()
        for job in jobs:
            TelegramJobPoster(job, my_states).post_job()
            sleep(1)
        sleep(10)


if __name__ == '__main__':
    main()
