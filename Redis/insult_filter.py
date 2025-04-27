import redis
import threading

class InsultFilter:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.work_queue = 'text_work_queue'
        self.filtered_texts = []

        threading.Thread(target=self._process_queue, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        insults = self.client.lrange('insult_service', 0, -1)  # Get all insults from Redis
        for insult in insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def append_text_filtering_work_queue(self, text):
        """Append text to the work queue for filtering"""
        self.client.rpush(self.work_queue, text)
        print(f"Text appended to work queue: {text}")

    def list_filtered_results(self):
        """List all filtered results"""
        return self.filtered_texts

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            text = self.client.blpop(self.work_queue, timeout=0)
            if text:
                original_text = text[1]
                filtered = self.filter_text(original_text)
                self.filtered_texts.append(filtered)
                print(f"Filtered: '{original_text}' → '{filtered}'")

