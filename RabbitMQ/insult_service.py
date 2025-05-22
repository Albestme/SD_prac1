import pika
import redis
import random
import multiprocessing
import threading  # <-- New import
from time import sleep
from RabbitMQ.subscriber import start_subscriber


class InsultService:
    def __init__(self):
        # Connect to RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Fanout exchange for broadcasting insults
        self.channel.exchange_declare(exchange='broadcast_channel', exchange_type='fanout')

        # Queue for receiving insults (direct queue)
        self.insult_queue = 'insult_queue'
        self.channel.queue_declare(queue=self.insult_queue, durable=True)

        # Shared list of insults
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']

        self.subscribers = []

        print("InsultService waiting for insults...")

        # Start threads/processes
        multiprocessing.Process(target=self._broadcast_random_insult, daemon=True).start()
        threading.Thread(target=self._listen_for_insults, daemon=True).start()  # <-- New listener thread

    def get_insults(self):
        return self.insults

    def add_insult(self, insult):
        """Add a new insult to the list"""
        if insult in self.insults:
            return "Insult already in list"
        else:
            self.insults.append(insult)
            return f"Insult added to list: {insult}"

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
                    body=insult.encode()
                )

    def _listen_for_insults(self):
        """Listen for insults arriving at the insult_queue"""

        def callback(ch, method, properties, body):
            insult = body.decode()
            print(f"Received new insult: {insult}")
            if insult not in self.insults:
                self.add_insult(insult)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Set QoS (optional): limit unacknowledged messages
        self.channel.basic_qos(prefetch_count=1)

        # Consume from the insult_queue
        self.channel.basic_consume(
            queue=self.insult_queue,
            on_message_callback=callback
        )

        print("Listening for insults...")
        self.channel.start_consuming()


def start_insult_server():
    InsultService()
    while True:
        sleep(10)


if __name__ == "__main__":
    start_insult_server()