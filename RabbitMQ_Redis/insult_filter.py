import pika
from time import sleep
import multiprocessing
import redis
import os

class InsultFilter:
    def __init__(self):
        self.filtered_texts = []

        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']

        self.connections = {}
        # Start the processing thread
        self.process_thread = multiprocessing.Process(target=self._process_queue, daemon=True)
        self.process_thread.start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSORED")

        return filtered

    def append_text_filtering_work_queue(self, text):
        """Append text to the work queue for filtering"""
        # Create a new connection for this operation
        pid = os.getpid()
        if not pid in self.connections:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            # Declare the queue to ensure it exists
            channel.queue_declare(queue='text_work_queue')
            self.connections[pid] = (pid, channel)
        else:
            channel = self.connections[pid][1]

        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key='text_work_queue',
            body=text
        )
        # print(f"Text appended to work queue: {text}")


    def list_filtered_results(self):
        """List all filtered results"""
        return self.filtered_texts

    def _process_queue(self):
        """Worker that processes the queue in background"""
        # Create a dedicated connection for this consumer thread
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='text_work_queue')

        # Set up consumer
        def callback(ch, method, properties, body):
            try:
                original_text = body.decode()
                filtered = self.filter_text(original_text)
                self.filtered_texts.append(filtered)
                print(f"Filtered: '{original_text}' → '{filtered}'")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")

        # Configure consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='text_work_queue',
            on_message_callback=callback,
            auto_ack=False  # Changed to False to handle errors properly
        )

        try:
            # Start consuming
            channel.start_consuming()
        except Exception as e:
            print(f"Consumer thread error: {e}")
        finally:
            connection.close()

def start_insult_filter():
    """Start the InsultFilter service"""
    InsultFilter()
    while True:
        sleep(10)


if __name__ == "__main__":
    start_insult_filter()