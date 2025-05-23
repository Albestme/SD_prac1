import pika

class MixedClient:
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

    def append_text_filtering_work_queue(self, text):
        """Send text to be filtered to text_work_queue"""
        self.channel.queue_declare(queue='text_work_queue')
        self.channel.basic_publish(
            exchange='',
            routing_key='text_work_queue',
            body=text.encode()
        )
        self.counter_filter += 1

