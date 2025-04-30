import pika
from time import sleep

def start_subscriber(subscriber_id):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange='broadcast_channel', exchange_type='fanout')

    # Create a new temporary queue (random name, auto-delete when consumer disconnects)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='broadcast_channel', queue=queue_name)

    print(f"Subscriber {subscriber_id} subscribed to broadcast_exchange, waiting for messages...")


    # Define the callback for receiving messages
    def callback(ch, method, properties, body):
        print(f"Subscriber {subscriber_id} received: {body.decode()}")

    # Set up the consumer
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()
