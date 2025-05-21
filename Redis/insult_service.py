import redis
import random
from time import sleep
import multiprocessing
from Redis.subscriber import start_subscriber
from redis.cluster import ClusterNode
import threading


class InsultService:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insult_list = "insult_list"
        self.insult_queue = 'insult_work_queue'
        self.broadcast_chanel = "broadcast_channel"
        self.subscribers = []
        self.insults = []

        threading.Thread(target=self._process_insult_queue).start()
        threading.Thread(target=self._broadcast_random_insult, daemon=True).start()

    # In a real distributed system I should request the insults to redis
    def get_insults(self):
        return self.insults

    def add_insult(self, insult):
        """Add a new insult to the list """
        if insult in self.insults:
            return "Insult already in redis list"
        else:
            self.insults.append(insult)
            self.client.rpush(self.insult_list, insult)
            return f"Insult added to redis list: {insult}"

    def register_subscriber(self, subscriber_id):
        """Start a new subscriber"""
        multiprocessing.Process(target=start_subscriber, args=(subscriber_id,)).start()
        self.subscribers.append(subscriber_id)
        print(f"Subscriber {subscriber_id} registered.")

    def _process_insult_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any insults in the queue
            insult = self.client.blpop(self.insult_queue, timeout=0)
            self.add_insult(insult)

    def _broadcast_random_insult(self):
        """Periodically broadcast random insults"""
        while True:
            sleep(5)  # Every 5 seconds
            insults = self.get_insults()
            if insults and self.subscribers:
                insult = random.choice(insults)
                print(f"Broadcasting insult: {insult}")
                self.client.publish(self.broadcast_chanel, insult)

if __name__ == "__main__":
    # Example usage
    service = InsultService()

    while True:
        sleep(5)
