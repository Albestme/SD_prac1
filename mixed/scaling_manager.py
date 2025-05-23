import pika
import uuid
import time
from time import sleep
import math
import multiprocessing
from mixed.insult_service import start_insult_server as insult_server
from mixed.insult_filter import start_insult_filter as filter_server


def calculate_needed_servers(arrival_rate, time_per_message, capacity):
    """Calculate the number of servers needed based on the number of insults"""
    return math.ceil(arrival_rate * time_per_message / capacity)


class ServerScalingManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.counter_insult = 0
        self.counter_filter = 0

        multiprocessing.Process(target=insult_server).start()
        multiprocessing.Process(target=filter_server).start()


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

    def monitor_insult_requests(self):
        """Monitor the number of insults sent to add/remove workers"""
        workers = 0
        servers = []
        check_interval = 1
        server_capacity = 1497.6786     # based on the single node benchmarks
        time_per_message = 0.000667
        previous_requests = 0
        while True:
            sleep(check_interval)
            requests = self.monitor_insult_requests()
            requests -= previous_requests
            previous_requests += requests
            arrival_rate = requests / server_capacity
            needed_workers = calculate_needed_servers(arrival_rate=arrival_rate, time_per_message=time_per_message,
                                                      capacity=server_capacity)
            if needed_workers > workers:
                increment = needed_workers - workers
                workers += increment
                print(f'incrementing to {workers} insult workers')
                for i in range(increment):
                    servers.append(multiprocessing.Process(target=insult_server))
                    servers[-1].start()
            elif needed_workers < workers:
                decrement = workers - needed_workers
                workers -= decrement
                print(f'decrementing to {workers} insult workers')
                for i in range(decrement):
                    servers[-1].terminate()
                    servers.pop(-1)


    def monitor_filter_requests(self):
        """Monitor the number of insults sent to add/remove workers"""
        workers = 0
        servers = []
        check_interval = 1
        server_capacity = 1588.65699  # based on the single node benchmarks
        time_per_message = 0.000629
        previous_requests = 0
        while True:
            sleep(check_interval)
            requests = self.monitor_filter_requests()
            requests -= previous_requests
            previous_requests += requests
            arrival_rate = requests / server_capacity
            needed_workers = calculate_needed_servers(arrival_rate=arrival_rate, time_per_message=time_per_message,
                                                      capacity=server_capacity)
            if needed_workers > workers:
                increment = needed_workers - workers
                workers += increment
                print(f'incrementing to {workers} filter workers')
                for i in range(increment):
                    servers.append(multiprocessing.Process(target=filter_server))
                    servers[-1].start()


            elif needed_workers < workers:
                decrement = workers - needed_workers
                workers -= decrement
                print(f'decrementing to {workers} filter workers')
                for i in range(decrement):
                    servers[-1].terminate()
                    servers.pop(-1)

    def close(self):
        """Close connection when done"""
        self.connection.close()