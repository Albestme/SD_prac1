import pika
import xmlrpc.client
import time
import random

def broadcast():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a fanout exchange named 'insults'
    channel.exchange_declare(exchange='insults', exchange_type='fanout')

    # Connect to the XML-RPC service
    service = xmlrpc.client.ServerProxy("http://localhost:8000/")

    try:
        while True:
            # Get the list of insults
            insults = service.list_insults()
            if insults:
                # Pick a random insult and send it through the 'insults' exchange
                message = random.choice(insults)
                channel.basic_publish(exchange='insults', routing_key='', body=message)
                print(f" [x] Broadcasted: {message}")
            time.sleep(5)
    finally:
        # Close the connection on exit
        connection.close()