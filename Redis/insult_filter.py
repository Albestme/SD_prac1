import multiprocessing
import threading
from time import sleep
import redis
import re



class InsultFilter:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Save insult list ot not overwhelm redis
        # In a real distributed system I should request the insults to redis
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
        self.filtered_queue = []
        self.text_work_queue = 'text_work_queue'
        self.requests_key = "filter_service_requests"
        self.requests = 0
        self._pattern = re.compile("|".join(map(re.escape, self.insults)))

        threading.Thread(target=self._process_queue, daemon=True).start()
        threading.Thread(target=self._monitor_requests, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        return self._pattern.sub("CENSORED", text)

    def _monitor_requests(self):
        logged_requests = 0
        while True:
            sleep(0.4)
            requests = self.requests
            if not logged_requests == requests:
                self.client.incrby(self.requests_key, requests-logged_requests)
                logged_requests = requests

    def _process_queue(self):
        """Worker that processes the queue in background"""
        counter = 0
        while True:
            # Process any texts in the queue
            text = self.client.blpop(self.text_work_queue, timeout=0)
            if text:
                original_text = text[1]
                filtered = self.filter_text(original_text)
                counter += 1
                if counter % 100 == 0:
                    self.requests += 100
                self.filtered_queue.append(filtered)
                #print(f"Filtered: '{original_text}' → '{filtered}'")


def start_insult_filter():
    InsultFilter()
    while True:
        sleep(10)

if __name__ == "__main__":
    # Start the insult filter service
    start_insult_filter()