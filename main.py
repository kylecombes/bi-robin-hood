import json
import requests
import threading
from time import sleep
from datetime import datetime


class BIRobinHood:

    sid_id = 194010443
    jon_id = 193788153

    data = {
        'entry_id': jon_id,
        'timestamp': 1532802805,
        # 'signature': 'e44fcefb7eea5a9a9180cf0da184ec57',
        # 'disable_restrictions': 'false',
        # 'fb_api_version': 2,
        # 'sim_time': '',
    }

    headers = {
        # 'Host': 'wayup.pgtb.me',
        # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'X-SS-URLPath': 'RnZkMG',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'X-SS-AVI': '821939440',
        # 'X-CSRF-Token': 'fQZE2O13RB1bQp5GyxdRUXvZpzdutJ7kka9YC0zDyME=',
        # 'X-SS-Token': 'vxwwn8RrvrNuYi0zUXNnZQ==',
        # 'X-SS-Timestamp': '1532804920',
        # 'Referer': 'https://wayup.pgtb.me/RnZkMG?embed=1&vOffset=0&autoscroll_p=1&app_data=referer_override%3D',
    }

    url = 'https://wayup.pgtb.me/facebook/vote/69148534'

    def __init__(self, concurrent_threads=20):
        self.status_update_interval = concurrent_threads * 4
        self.threading_lock = threading.Lock()
        self.success_count = 0
        self.failure_count = 0
        self.last_checkin_at_time = datetime.now()
        self.last_checkin_at_count = 0

        main_thread = threading.current_thread()
        for _ in range(concurrent_threads):
            t = threading.Thread(target=self.make_requests_while_active)
            t.start()

        # Wait till all threads finish before continuing
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

    def callback(self, response):
        self.threading_lock.acquire()
        success = response.status_code == 200 and 'error' not in response.text
        if success:
            self.success_count += 1
            if self.success_count % self.status_update_interval == 0:
                current_vote_count = json.loads(response.text).get('votes')
                print(self.success_count, 'successful requests made. Vote currently at', current_vote_count)
                elapsed_time = datetime.now() - self.last_checkin_at_time
                requests_made_since_checkin = self.success_count - self.last_checkin_at_count
                requests_per_second = requests_made_since_checkin / max(elapsed_time.seconds, 1e-6)
                print('Current successful request rate: {:0.2f} requests/second'.format(requests_per_second))
                self.last_checkin_at_count = self.success_count
                self.last_checkin_at_time = datetime.now()
        else:
            self.failure_count += 1
            print('Casting vote failed:')
            print(response.text)
            sleep(2)
        self.threading_lock.release()

    def make_requests_while_active(self):
        try:
            res = requests.get(self.url, data=self.data, headers=self.headers)
            self.callback(res)
        except:
            print('Houston, we had a problem. Sleeping for 5s...')
            sleep(5)


if __name__ == '__main__':
    BIRobinHood(concurrent_threads=50)
