import pika
import redis
import random
import multiprocessing
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
        print("InsultService waiting for insults...")

        # Start a redis queue to store insults
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']

        # Start broadcasting thread
        multiprocessing.Process(target=self._broadcast_random_insult, daemon=True).start()


    def get_insults(self):
        return self.insults

    def add_insult(self, insult):
        """Add a new insult to the list"""
        if insult in self.insults:
            return "Insult already in redis list"
        else:
            self.insults.append(insult)
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

                # Publish to the fanout exchange
                self.channel.basic_publish(
                    exchange='broadcast_channel',
                    routing_key='',  # With fanout, routing key is ignored
                    body=insult
                )


def start_insult_server():
    InsultService()
    while True:
        sleep(10)

if __name__ == "__main__":
    start_insult_server()