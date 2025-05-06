import pika
import redis
import random
import threading
from time import sleep
from RabbitMQ_Redis.subscriber import start_subscriber


class InsultService:
    def __init__(self):
        # Connect to RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Create fanout exchange
        self.channel.exchange_declare(exchange='broadcast channel', exchange_type='fanout')

        self.subscribers = []
        self.insults = []
        print("InsultService waiting for insults...")

        # Start a redis queue to store insults
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insult_channel = "insult_list"

        # Start broadcasting thread
        threading.Thread(target=self._broadcast_random_insult, daemon=True).start()


    def get_insults(self):
        return self.redis.lrange(self.insult_channel, 0, -1)

    def add_insult(self, insult):
        """Add a new insult to the list"""
        insults = self.get_insults()
        if insult in insults:
            print("Insult already in redis list")
        else:
            self.redis.rpush(self.insult_channel, insult)
            print(f"Insult added to redis list: {insult}")

    def register_subscriber(self, subscriber_id):
        """Start a new subscriber"""
        threading.Thread(target=start_subscriber, args=(subscriber_id,)).start()
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

                # Publish to the fanout exchange
                self.channel.basic_publish(
                    exchange='broadcast_channel',
                    routing_key='',  # With fanout, routing key is ignored
                    body=insult
                )


if __name__ == "__main__":
    InsultService()
    try:
        # Keep the program running
        print("Service started. Press CTRL+C to exit.")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down service...")
