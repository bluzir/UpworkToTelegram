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
        my_states = StateManager('states')
        my_upwork_feed = RSSManager()
        my_upwork_feed.parse_feed()
        my_jobs = JobManager(my_upwork_feed, my_states)
        while True:
            jobs = my_jobs.get_new_jobs()
            for job in jobs:
                TelegramJobPoster(job).post_job()
                sleep(1)
            sleep(30)
    else:
        logging.info('Invalid token')
        pass


if __name__ == '__main__':
    main()
