import logging


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
            logging.info('No new jobs available, waiting')
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

        jobs = self.rss.feed['entries']
        self.state.add_value_by_key('last_link', jobs[0].link)
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