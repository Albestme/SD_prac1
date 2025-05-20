import redis
import random
from time import sleep
import multiprocessing
from Redis.subscriber import start_subscriber
from redis.cluster import ClusterNode


class InsultService:
    def __init__(self):
        self.client = redis.cluster.RedisCluster(startup_nodes=[
            ClusterNode('172.28.0.2', '6379'),
            ClusterNode('172.28.0.3', '6379'),
            ClusterNode('172.28.0.4', '6379')],
            decode_responses=True)
        self.insult_channel = "insult_service"
        self.broadcast_chanel = "broadcast_channel"
        self.subscribers = []

        #multiprocessing.Process(target=self._broadcast_random_insult, daemon=True).start()

    def get_insults(self):
        return self.client.lrange(self.insult_channel, 0, -1)

    def add_insult(self, insult):
        """Add a new insult to the list """
        insults = self.get_insults()
        if insult in insults:
            return "Insult already in redis list"
        else:
            self.client.rpush(self.insult_channel, insult)
            return f"Insult added to redis list: {insult}"

    def register_subscriber(self, subscriber_id):
        """Start a new subscriber"""
        multiprocessing.Process(target=start_subscriber, args=(subscriber_id,)).start()
        self.subscribers.append(subscriber_id)
        print(f"Subscriber {subscriber_id} registered.")

    def _broadcast_random_insult(self):
        """Periodically broadcast random insults"""
        while True:
            sleep(5)  # Every 5 seconds
            insults = self.get_insults()
            if insults and self.subscribers:
                insult = random.choice(insults)
                print(f"Broadcasting insult: {insult}")
                self.client.publish(self.broadcast_chanel, insult)
