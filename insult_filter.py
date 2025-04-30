import pika
import redis
import xmlrpc.client

class InsultFilter:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insults_key = "insults"           # same key used by InsultService
        self.filtered_key = "filtered_texts"
        self.rpc_service = xmlrpc.client.ServerProxy("http://localhost:8000/")

        # RabbitMQ connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.queue_name = "text_filter"
        self.channel.queue_declare(queue=self.queue_name)

    def list_filtered_results(self):
        return list(self.redis_client.lrange(self.filtered_key, 0, -1))

    def _censor_text(self, text):
        # Get insults via Redis or XML-RPC
        insults = self.redis_client.smembers(self.insults_key)
        # If needed, fetch from XML-RPC instead:
        # insults = self.rpc_service.list_insults()
        for insult in insults:
            text = text.replace(insult, "CENSORED")
        return text

    def _callback(self, ch, method, properties, body):
        text = body.decode()
        censored = self._censor_text(text)
        self.redis_client.rpush(self.filtered_key, censored)
        print(f"Received: {text} -> Censored: {censored}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_filter(self):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback)
        print("Filter is running... Waiting for messages.")
        self.channel.start_consuming()

if __name__ == "__main__":
    filter_service = InsultFilter()
    filter_service.start_filter()