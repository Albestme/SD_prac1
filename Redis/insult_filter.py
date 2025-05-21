import redis
import multiprocessing
from redis.cluster import ClusterNode
import threading



class InsultFilter:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Save insult list ot not overwhelm redis
        # In a real distributed system I should request the insults to redis
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
        self.filtered_queue = 'text_filtered_queue'
        self.text_work_queue = 'text_work_queue'

        threading.Thread(target=self._process_queue, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            text = self.client.blpop(self.text_work_queue, timeout=0)
            if text:
                original_text = text[1]
                filtered = self.filter_text(original_text)
                self.client.rpush(self.filtered_queue, filtered)
                #print(f"Filtered: '{original_text}' → '{filtered}'")

