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
    print(f"{arrival_rate * time_per_message / capacity:.2f}")
    return math.ceil(arrival_rate * time_per_message / capacity)


class ServerScalingManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.counter_insult = 0
        self.counter_filter = 0

        self.insult_processes = []
        self.filter_processes = []
        self.insult_processes.append(multiprocessing.Process(target=insult_server))
        self.insult_processes[-1].start()
        self.filter_processes.append(multiprocessing.Process(target=filter_server))
        self.filter_processes[-1].start()
        multiprocessing.Process(target=self.monitor_insult_requests).start()
        multiprocessing.Process(target=self.monitor_filter_requests).start()


    def add_insult(self, insult):
        """Send an insult to the insult_queue"""
        self.channel.queue_declare(queue='insult_queue', durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='insult_queue',
            body=insult.encode(),
        )
        self.counter_insult += 1

    def append_text_filtering_work_queue(self, text):
        """Send text to be filtered to text_work_queue"""
        self.channel.queue_declare(queue='text_work_queue')
        self.channel.basic_publish(
            exchange='',
            routing_key='text_work_queue',
            body=text.encode()
        )
        self.counter_filter += 1

    def get_queue_length(self, queue_name):
        """Returns the number of messages in a queue"""
        response = self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            passive=True  # Only check if queue exists
        )
        return response.method.message_count

    def monitor_queue(self, queue_name, process_list, server_target, worker_capacity, time_per_message, label):
        check_interval = 1
        while True:
            sleep(check_interval)
            queue_len = self.get_queue_length(queue_name)
            print(f"[{label}] Messages in queue: {queue_len}")

            arrival_rate = queue_len / check_interval
            needed_workers = math.ceil(arrival_rate * time_per_message / worker_capacity)

            current_workers = len(process_list)
            print(
                f'[{label}] Current workers: {current_workers} | Arrival rate: {arrival_rate:.2f} | Needed: {needed_workers}')

            # Scale up
            while len(process_list) < needed_workers:
                p = multiprocessing.Process(target=server_target)
                p.start()
                process_list.append(p)
                print(f"Started new {label} server, total: {len(process_list)}")

            # Scale down
            while len(process_list) > needed_workers > 0:
                p = process_list.pop()
                p.terminate()
                p.join(timeout=0.5)
                print(f"Stopped a {label} server, remaining: {len(process_list)}")

    def monitor_insult_requests(self):
        self.monitor_queue(
            queue_name='insult_queue',
            process_list=self.insult_processes,
            server_target=insult_server,
            worker_capacity=1497.6786,
            time_per_message=0.000667,
            label="Insult"
        )

    def monitor_filter_requests(self):
        self.monitor_queue(
            queue_name='text_work_queue',
            process_list=self.filter_processes,
            server_target=filter_server,
            worker_capacity=1588.65699,
            time_per_message=0.000629,
            label="Filter"
        )
    def close(self):
        """Close connection when done"""
        self.connection.close()