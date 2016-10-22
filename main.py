# -*- coding:utf-8 -*-
import logging
from time import sleep


from jobs import JobManager
from rss import RSSManager
from states import StateManager
from telegram import TelegramAPIManager, TelegramJobPoster

logging.basicConfig(level=logging.INFO)


def main():
    if TelegramAPIManager().check_token():
        logging.info('Start working')
        states = StateManager('states')
        upwork_feed = RSSManager()
        upwork_feed.parse_feed()
        upwork_jobs = JobManager(upwork_feed, states)
        while True:
            jobs = upwork_jobs.get_new_jobs()
            for job in jobs:
                TelegramJobPoster(job).post_job()
                sleep(1)
            sleep(30)
    else:
        logging.info('Invalid token')
        pass


if __name__ == '__main__':
    main()
