import pika
from time import sleep, time
import multiprocessing
import threading
import uuid


class InsultFilter:
    def __init__(self):
        self.filtered_texts = []
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
        self.filtered_count = 0  # Counter for processed texts
        self.connections = {}

        # Setup RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Fanout exchange for broadcasting count requests
        self.channel.exchange_declare(exchange='filter_request_exchange', exchange_type='fanout')

        # Each instance has a unique private queue for replies
        self.server_id = str(uuid.uuid4())
        self.private_queue = self.channel.queue_declare(queue='').method.queue
        self.channel.queue_bind(exchange='filter_request_exchange', queue=self.private_queue)

        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.process_thread.start()
        threading.Thread(target=self._listen_for_filter_requests, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def list_filtered_results(self):
        """List all filtered results"""
        return self.filtered_texts

    def _process_queue(self):
        """Worker that processes the queue in background"""
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='text_work_queue')

        def callback(ch, method, properties, body):
            try:
                original_text = body.decode()
                filtered = self.filter_text(original_text)
                self.filtered_texts.append(filtered)
                self.filtered_count += 1  # Increment counter
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='text_work_queue',
            on_message_callback=callback,
            auto_ack=False
        )

        try:
            channel.start_consuming()
        finally:
            connection.close()

    def _listen_for_filter_requests(self):
        """Listen for global count requests via fanout exchange"""
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        def callback(ch, method, props, body):
            if body.decode() == 'get_filtered_count':
                ch.basic_publish(
                    exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(correlation_id=props.correlation_id),
                    body=str(self.filtered_count)
                )
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=self.private_queue, on_message_callback=callback, auto_ack=False)
        print("Filter service is listening for count queries...")
        channel.start_consuming()


def start_insult_filter():
    """Start the InsultFilter service"""
    InsultFilter()
    while True:
        sleep(10)


if __name__ == "__main__":
    start_insult_filter()