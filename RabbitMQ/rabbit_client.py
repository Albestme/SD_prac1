import pika
import uuid
import time
from time import sleep


class RabbitMQClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.counter_insult = 0
        self.counter_filter = 0

    def add_insult(self, insult):
        """Send an insult to the insult_queue"""
        self.channel.queue_declare(queue='insult_queue', durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='insult_queue',
            body=insult.encode(),
        )
        self.counter_insult += 1
        print(f"Submitted insult to queue {self.counter_insult}")

    def append_text_filtering_work_queue(self, text):
        """Send text to be filtered to text_work_queue"""
        self.channel.queue_declare(queue='text_work_queue')
        self.channel.basic_publish(
            exchange='',
            routing_key='text_work_queue',
            body=text.encode()
        )
        self.counter_filter += 1

    def get_insult_request_count(self):
        corr_id = str(uuid.uuid4())
        callback_queue = self.channel.queue_declare(queue='').method.queue

        # Prepare to collect responses
        responses = []
        def on_response(ch, method, props, body):
            if props.correlation_id == corr_id:
                responses.append(int(body))

        self.channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

        # Send the broadcast
        print("Broadcasting request for request count...")
        self.channel.basic_publish(
            exchange='request_count_exchange',
            routing_key='',  # Fanout ignores routing key
            body='get_request_count',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id
            )
        )

        # Wait until we've received some responses (or timeout after N seconds)
        timeout = 5
        start_time = time.time()
        while len(responses) == 0 and time.time() - start_time < timeout:
            self.connection.process_data_events()

        return sum(responses)

    def get_filter_filtered_count(self):
        corr_id = str(uuid.uuid4())
        callback_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        responses = []

        def on_response(ch, method, props, body):
            if props.correlation_id == corr_id:
                responses.append(int(body))

        self.channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

        # Send the broadcast
        self.channel.basic_publish(
            exchange='filter_request_exchange',
            routing_key='',  # Fanout ignores routing key
            body='get_filtered_count',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id
            )
        )

        # Wait for responses (with timeout)
        timeout = 5
        start_time = time.time()
        while len(responses) == 0 and time.time() - start_time < timeout:
            self.connection.process_data_events()

        total = sum(responses)
        return total

    def wait_insult_requests_processing(self, iterations):
        while True:
            sleep(0.1)
            processed = self.get_insult_request_count()
            print(processed, ' ', iterations)
            if int(processed) >= iterations:
                break

    def wait_filter_requests_processing(self, iterations):
        while True:
            sleep(0.1)
            processed = self.get_filter_filtered_count()
            if int(processed) >= iterations:
                break

    def close(self):
        """Close connection when done"""
        self.connection.close()
