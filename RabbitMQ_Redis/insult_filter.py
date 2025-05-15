import pika
from time import sleep
import multiprocessing
import threading
import redis

class InsultFilter:
    def __init__(self):
        self.filtered_texts = []
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Start the processing thread
        self.process_thread = multiprocessing.Process(target=self._process_queue, daemon=True)
        self.process_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.process_thread.start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        insults = self.redis.lrange('insult_list', 0, -1)

        for insult in insults:
            filtered = filtered.replace(insult, "CENSORED")

        return filtered

    def append_text_filtering_work_queue(self, text):
        """Append text to the work queue for filtering"""
        # Create a new connection for this operation
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue to ensure it exists
        channel.queue_declare(queue='text_work_queue')

        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key='text_work_queue',
            body=text
        )
        print(f"Text appended to work queue: {text}")

        # Close the connection
        connection.close()

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

if __name__ == "__main__":
    filter_service = InsultFilter()
    try:
        # Keep the program running
        print("Service started. Press CTRL+C to exit.")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down service...")

