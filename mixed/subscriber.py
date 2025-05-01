import functools

import pika

def callback(ch, method, properties, body, subscriber_id):
    print(f"Subscriber {subscriber_id} receeived insult: {body.decode()}")

def start_subscriber(subscriber_id):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange='insults', exchange_type='fanout')

    # Create a temporary queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange
    channel.queue_bind(exchange='insults', queue=queue_name)

    # Create a partial function with subscriber_id bound
    bound_callback = functools.partial(callback, subscriber_id=subscriber_id)

    channel.basic_consume(queue=queue_name, on_message_callback=bound_callback, auto_ack=True)

    print("Listening for insults...")
    channel.start_consuming()