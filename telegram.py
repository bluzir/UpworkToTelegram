import logging

import requests

from settings import CHAT_ID, TELEGRAM_BOT_TOKEN


class TelegramAPIManager:
    telegram_bot_api_url = 'https://api.telegram.org/bot{}/{}'
    parse_mode = 'markdown'
    chat_id = CHAT_ID
    token = TELEGRAM_BOT_TOKEN
    params = {
        'chat_id': chat_id,
        'parse_mode': parse_mode,
    }

    def check_token(self):
        try:
            full_url = self.telegram_bot_api_url.format(TELEGRAM_BOT_TOKEN, 'getMe')
            response = requests.get(url=full_url)
            decode = response.json()
            if decode['ok']:
                return True
            else:
                return False
        except Exception as e:
            logging.warning(e)
            return False

    def send_message(self, text):
        self.params.update({'text': text})
        full_url = self.telegram_bot_api_url.format(TELEGRAM_BOT_TOKEN, 'sendMessage')
        try:
            response = requests.get(url=full_url, params=self.params)
            decode = response.json()
            if decode['ok']:
                logging.info('Successfully sent message')
            else:
                logging.debug(decode['error_code'], decode['description'])
                logging.info('Cant send a message')
        except Exception as e:
            logging.debug(e)


class TelegramJobPoster(TelegramAPIManager):
    def __init__(self, job):
        self.job = job
        self.formatted = None

    def format_job_to_message(self):
        self.formatted = "{}\n[Cсылка]({})\n".format(self.job.title, self.job.link)

    def post_job(self):
        if not self.formatted:
            self.format_job_to_message()
        self.send_message(self.formatted)