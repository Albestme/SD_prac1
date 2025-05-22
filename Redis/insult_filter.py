import redis
import multiprocessing
from redis.cluster import ClusterNode
import threading
from time import sleep



class InsultFilter:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Save insult list ot not overwhelm redis
        # In a real distributed system I should request the insults to redis
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
        self.filtered_queue = 'text_filtered_queue'
        self.text_work_queue = 'text_work_queue'
        self.requests_key = "filter_service_requests"
        self.requests = 0

        threading.Thread(target=self._process_queue, daemon=True).start()
        threading.Thread(target=self._monitor_requests, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def _monitor_requests(self):
        logged_requests = 0
        while True:
            sleep(0.1)
            requests = self.requests
            if not logged_requests == requests and requests % 10 == 0:
                self.client.incrby(self.requests_key, requests-logged_requests)
                logged_requests = requests

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            text = self.client.blpop(self.text_work_queue, timeout=0)
            if text:
                original_text = text[1]
                filtered = self.filter_text(original_text)
                self.requests += 1
                self.client.rpush(self.filtered_queue, filtered)
                #print(f"Filtered: '{original_text}' → '{filtered}'")


def start_insult_filter():
    InsultFilter()
    while True:
        sleep(10)